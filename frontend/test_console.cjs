const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error' && !msg.text().includes('favicon.ico')) {
      errors.push(msg.text());
    }
  });
  page.on('pageerror', err => {
    errors.push(err.toString());
  });

  console.log("Acessando http://localhost:5173...");
  await page.goto('http://localhost:5173', { waitUntil: 'networkidle2' });
  
  try {
    console.log("Fazendo upload...");
    const fileInput = await page.$('input[type="file"]');
    await fileInput.uploadFile(path.resolve(__dirname, '../backend/test_data.csv'));
    
    // Clica em 'Diagnosticar e limpar'
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const btn = btns.find(b => b.textContent.includes('Diagnosticar e limpar'));
      if(btn) btn.click();
    });
    
    // Espera Step 2 aparecer
    console.log("Esperando Step 2...");
    await new Promise(r => setTimeout(r, 4000));
    
    // Clica em Continuar para Revisão
    console.log("Clicando em Continuar para Revisão...");
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const btn = btns.find(b => b.textContent.includes('Revisão'));
      if(btn) btn.click();
    });
    
    // Espera Step 3
    console.log("Esperando Step 3...");
    await new Promise(r => setTimeout(r, 3000));
    
    // Clica em Aplicar decisões
    console.log("Clicando em Aplicar Decisões...");
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button'));
      const btn = btns.find(b => b.textContent.includes('Aplicar decisões'));
      if(btn) btn.click();
    });
    
    // Espera Step 4 (Gráficos)
    console.log("Esperando Step 4 (Gráficos)...");
    await new Promise(r => setTimeout(r, 8000));
    
    console.log("Tirando print da tela final...");
    await page.screenshot({ path: 'test_step4.png', fullPage: true });

  } catch(e) {
    console.log("Erro na automação:", e.message);
  }

  if (errors.length > 0) {
    console.log("\nERROS DE CONSOLE ENCONTRADOS:");
    errors.forEach(e => console.log(e));
  } else {
    console.log("\nNenhum erro de Javascript detectado no console!");
  }
  
  await browser.close();
})();
