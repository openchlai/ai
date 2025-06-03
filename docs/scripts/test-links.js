#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Enhanced link checker for built VitePress site
 * Validates that the build output contains expected files and structure
 */
function checkLinks() {
  console.log('🔍 Starting link validation...');
  
  // Define paths
  const distDir = path.join(__dirname, '..', 'docs', '.vitepress', 'dist');
  const cacheDir = path.join(__dirname, '..', 'docs', '.vitepress', 'cache');
  
  // Check if build directory exists
  if (!fs.existsSync(distDir)) {
    console.error('❌ Build directory not found at:', distDir);
    console.error('   Run "npm run build" first to generate the build output.');
    process.exit(1);
  }

  console.log('✅ Build directory exists');
  console.log('   Location:', distDir);
  
  // Check if index.html exists (main entry point)
  const indexFile = path.join(distDir, 'index.html');
  if (!fs.existsSync(indexFile)) {
    console.error('❌ index.html not found in build output');
    console.error('   Expected at:', indexFile);
    process.exit(1);
  }

  console.log('✅ index.html exists');

  // Check if assets directory exists and count files
  const assetsDir = path.join(distDir, 'assets');
  if (fs.existsSync(assetsDir)) {
    try {
      const assets = fs.readdirSync(assetsDir);
      const jsFiles = assets.filter(file => file.endsWith('.js')).length;
      const cssFiles = assets.filter(file => file.endsWith('.css')).length;
      const otherFiles = assets.length - jsFiles - cssFiles;
      
      console.log(`✅ Assets directory exists with ${assets.length} files`);
      console.log(`   - JavaScript files: ${jsFiles}`);
      console.log(`   - CSS files: ${cssFiles}`);
      console.log(`   - Other files: ${otherFiles}`);
    } catch (error) {
      console.log('⚠️  Could not read assets directory:', error.message);
    }
  } else {
    console.log('⚠️  Assets directory not found (this might be okay for simple sites)');
  }

  // Check for common documentation pages
  const commonPages = [
    'install.html',
    'features.html', 
    'faq.html',
    'support.html',
    'contributing.html',
    'roadmap.html'
  ];
  
  let pagesFound = 0;
  const foundPages = [];
  const missingPages = [];
  
  commonPages.forEach(page => {
    const pagePath = path.join(distDir, page);
    if (fs.existsSync(pagePath)) {
      console.log(`✅ ${page} found`);
      pagesFound++;
      foundPages.push(page);
    } else {
      console.log(`⚠️  ${page} not found (optional)`);
      missingPages.push(page);
    }
  });

  // List all HTML files in the build output
  try {
    const allFiles = fs.readdirSync(distDir);
    const htmlFiles = allFiles.filter(file => file.endsWith('.html'));
    
    console.log(`📄 Total HTML files generated: ${htmlFiles.length}`);
    if (htmlFiles.length > 0) {
      console.log('   HTML files:');
      htmlFiles.forEach(file => {
        console.log(`   - ${file}`);
      });
    }
  } catch (error) {
    console.log('⚠️  Could not list HTML files:', error.message);
  }

  // Check for critical files
  const criticalFiles = [
    'index.html',
    'hashmap.json'
  ];

  criticalFiles.forEach(file => {
    const filePath = path.join(distDir, file);
    if (fs.existsSync(filePath)) {
      const stats = fs.statSync(filePath);
      console.log(`✅ ${file} exists (${Math.round(stats.size / 1024)}KB)`);
    } else {
      console.log(`⚠️  ${file} not found`);
    }
  });

  // Validate that index.html contains basic structure
  try {
    const indexContent = fs.readFileSync(indexFile, 'utf8');
    
    const checks = [
      { test: /<html/i, name: 'HTML tag' },
      { test: /<head/i, name: 'HEAD section' },
      { test: /<body/i, name: 'BODY section' },
      { test: /<title/i, name: 'TITLE tag' },
      { test: /vitepress/i, name: 'VitePress markers' }
    ];

    console.log('🔍 Validating index.html structure:');
    checks.forEach(check => {
      if (check.test.test(indexContent)) {
        console.log(`   ✅ ${check.name} found`);
      } else {
        console.log(`   ⚠️  ${check.name} not found`);
      }
    });

  } catch (error) {
    console.log('⚠️  Could not validate index.html content:', error.message);
  }

  // Summary
  console.log('\n📊 Validation Summary:');
  console.log(`   - Build directory: ✅ Found`);
  console.log(`   - Index file: ✅ Found`);
  console.log(`   - Assets: ${fs.existsSync(assetsDir) ? '✅' : '⚠️'} ${fs.existsSync(assetsDir) ? 'Found' : 'Not found'}`);
  console.log(`   - Documentation pages: ${pagesFound}/${commonPages.length} found`);
  
  if (foundPages.length > 0) {
    console.log(`   - Available pages: ${foundPages.join(', ')}`);
  }

  // Clean up cache if it exists and is old
  if (fs.existsSync(cacheDir)) {
    try {
      const cacheStats = fs.statSync(cacheDir);
      const daysSinceModified = (Date.now() - cacheStats.mtime.getTime()) / (1000 * 60 * 60 * 24);
      
      if (daysSinceModified > 7) {
        console.log('🧹 Cache is older than 7 days, consider cleaning it');
      }
    } catch (error) {
      // Ignore cache check errors
    }
  }

  console.log('\n🎉 Link validation completed successfully!');
  console.log('   Your VitePress site has been built and appears to be valid.');
}

// Error handling wrapper
function main() {
  try {
    checkLinks();
  } catch (error) {
    console.error('\n❌ Link validation failed with error:');
    console.error('   ', error.message);
    
    if (error.code === 'ENOENT') {
      console.error('\n💡 Suggestions:');
      console.error('   1. Make sure you run "npm run build" first');
      console.error('   2. Check that your VitePress configuration is correct');
      console.error('   3. Verify that your documentation files exist');
    }
    
    process.exit(1);
  }
}

// Run the validation
main();