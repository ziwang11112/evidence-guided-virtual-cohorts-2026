const fs=require('fs');
const path=require('path');
const {pathToFileURL,fileURLToPath}=require('url');
const {chromium}=require('playwright');
(async()=>{
 const root=__dirname, out=path.join(root,'qa');
 fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,...(process.env.CHROME_EXECUTABLE_PATH ? {executablePath:process.env.CHROME_EXECUTABLE_PATH} : {channel:'chrome'})});
 const page=await browser.newPage({viewport:{width:1440,height:1080},deviceScaleFactor:1});
 const errors=[],blocked=[],checks=[];
 page.on('pageerror',e=>errors.push(String(e)));
 page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
 await page.route(/^https?:\/\//,r=>{blocked.push(r.request().url());return r.abort();});
 await page.goto(pathToFileURL(path.join(root,'index.html')).href);
 await page.locator('#node-detail h3').waitFor();
 await page.screenshot({path:path.join(out,'desktop-overview.png'),fullPage:true});
 for(const id of ['task','evidence','agent','generation','release','skill','harness','isolation']){
  await page.locator('[data-node="'+id+'"]').click();
  if(!(await page.locator('#node-detail h3').textContent()))throw Error('Missing detail '+id);
 }
 checks.push('8 architecture details');
 for(const id of ['overview','walk','components','validation','contribution']){
  await page.locator('#tab-'+id).click();
  if(!(await page.locator('#'+id).isVisible()))throw Error('Tab not visible '+id);
  const visible=await page.locator('[role=tabpanel]:visible').count();
  if(visible!==1)throw Error('Visible panel count '+visible);
 }
 checks.push('5 tabs');
 await page.locator('#tab-walk').click();
 let states=0;
 for(const mode of ['enrichment','whole','completion']){
  await page.locator('[data-mode="'+mode+'"]').click();
  for(const route of ['program','direct']){
   await page.locator('[data-route="'+route+'"]').click();
   for(let step=0;step<8;step++){
    await page.locator('[data-step="'+step+'"]').click();
    const title=await page.locator('#walk-content h3').textContent();
    if(!title.startsWith(String(step+1).padStart(2,'0')))throw Error('Wrong walkthrough');
    if(await page.locator('#prev').isDisabled()!==(step===0))throw Error('Previous boundary');
    if(await page.locator('#next').isDisabled()!==(step===7))throw Error('Next boundary');
    states++;
   }
  }
 }
 checks.push(states+' walkthrough combinations');
 await page.locator('[data-mode="enrichment"]').click();
 await page.locator('[data-route="program"]').click();
 await page.locator('[data-step="3"]').click();
 await page.screenshot({path:path.join(out,'desktop-walkthrough.png'),fullPage:true});
 await page.locator('#tab-overview').click();
 await page.locator('[data-node="agent"]').click();
 await page.locator('.diagram-open summary').click();
 const img=page.locator('.diagram-container img');
 await img.scrollIntoViewIfNeeded();
 await page.waitForFunction(()=>{const i=document.querySelector('.diagram-container img');return i.complete&&i.naturalWidth>0;});
 await img.screenshot({path:path.join(out,'architecture-render.png')});
 checks.push('embedded SVG loaded offline');
 await page.locator('.diagram-open summary').click();
 const links=await page.locator('a').evaluateAll(a=>a.map(x=>x.getAttribute('href')));
 const missing=[];
 for(const href of links){
  if(!href||/^(https?:|#|data:)/.test(href))continue;
  if(!fs.existsSync(path.resolve(root,decodeURIComponent(href))))missing.push(href);
 }
 if(missing.length)throw Error('Missing local links: '+missing.join(','));
 checks.push('all local links exist');
 await page.setViewportSize({width:390,height:844});
 await page.locator('#tab-overview').click();
 await page.screenshot({path:path.join(out,'mobile-overview.png'),fullPage:true});
 const overflows=[];
 for(const width of [320,390,768,1440]){
  await page.setViewportSize({width,height:900});
  for(const id of ['overview','walk','components','validation','contribution']){
   await page.locator('#tab-'+id).click();
   const dim=await page.evaluate(()=>({w:innerWidth,scroll:document.documentElement.scrollWidth}));
   if(dim.scroll>dim.w+1)overflows.push({width,id,...dim});
  }
 }
 if(overflows.length)throw Error('Horizontal overflow '+JSON.stringify(overflows));
 checks.push('20 viewport/panel combinations no page overflow');
 await page.setViewportSize({width:1440,height:1080});
 await page.locator('#tab-overview').click();
 await page.locator('#tab-overview').focus();
 await page.keyboard.press('ArrowRight');
 if(await page.locator('#tab-walk').getAttribute('aria-selected')!=='true')throw Error('Keyboard tab failure');
 checks.push('keyboard tab navigation');
 await page.emulateMedia({media:'print'});
 if(await page.locator('[role=tabpanel]:visible').count()!==5)throw Error('Print missing panels');
 await page.pdf({path:path.join(out,'print-preview.pdf'),format:'A4',printBackground:true,margin:{top:'12mm',bottom:'12mm',left:'10mm',right:'10mm'}});
 checks.push('all five panels available in print');
 await page.emulateMedia({media:'screen'});
 const report={pass:errors.length===0,checks,errors,networkRequests:blocked,missingLocalLinks:missing};
 fs.writeFileSync(path.join(out,'qa-report.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify(report));
 await browser.close();
 if(errors.length||blocked.length)process.exit(1);
})().catch(e=>{console.error(e);process.exit(1);});
