<template>
  <div class="settings-wrapper">
    <button class="mobile-menu-btn" id="mobile-menu-btn" @click="toggleMobileMenu">
      <svg fill="none" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 12H21M3 6H21M3 18H21" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
      </svg>
    </button>

    <SidePanel :userRole="userRole" :isInQueue="isInQueue" :isProcessingQueue="isProcessingQueue" :currentCall="currentCall" @toggle-queue="handleQueueToggle" @logout="handleLogout" @sidebar-toggle="handleSidebarToggle" />

    <div class="main-content" :style="{ marginLeft: mainContentMarginLeft }">
      <div class="header">
        <button class="sidebar-toggle" @click="toggleSidebar">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 6H20M4 12H20M4 18H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <h1>Settings</h1>
        <p>Customize your experience and preferences</p>
      </div>

      <div class="settings-container">
        <!-- Appearance Settings -->
        <div class="settings-section">
          <div class="settings-section-header">
            <div class="settings-section-title">Appearance</div>
            <div class="settings-section-description">Customize how the application looks</div>
          </div>
          <div class="settings-option">
            <div>
              <div class="option-label">Theme</div>
              <div class="option-description">Choose between light and dark mode</div>
            </div>
            <div class="toggle-switch">
              <input id="theme-toggle" type="checkbox" />
              <span class="toggle-slider"></span>
            </div>
          </div>
          <div class="settings-option">
            <div>
              <div class="option-label">Font Size</div>
              <div class="option-description">Adjust the size of text throughout the application</div>
            </div>
            <div class="select-wrapper">
              <select class="settings-select" id="font-size">
                <option value="small">Small</option>
                <option value="medium">Medium</option>
                <option value="large">Large</option>
              </select>
              <div class="select-arrow">
                <svg fill="none" height="6" viewBox="0 0 12 6" width="12" xmlns="http://www.w3.org/2000/svg">
                  <path d="M1 1L6 5L11 1" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" />
                </svg>
              </div>
            </div>
          </div>
          <div class="settings-option">
            <div>
              <div class="option-label">High Contrast</div>
              <div class="option-description">Enable high-contrast mode for better visibility</div>
            </div>
            <div class="toggle-switch">
              <input id="high-contrast-toggle" type="checkbox" />
              <span class="toggle-slider"></span>
            </div>
          </div>
          <div class="settings-option">
            <div>
              <div class="option-label">Read Aloud</div>
              <div class="option-description">Read this page aloud for accessibility</div>
            </div>
            <button class="btn btn-secondary" @click="readAloud">{{ isReading ? 'Stop Read Aloud' : 'Read Aloud' }}</button>
          </div>
        </div>

        <!-- Notification Settings -->
        <div class="settings-section">
          <div class="settings-section-header">
            <div class="settings-section-title">Notifications</div>
            <div class="settings-section-description">Manage your notification preferences</div>
          </div>
          <div class="settings-option">
            <div>
              <div class="option-label">Email Notifications</div>
              <div class="option-description">Receive email notifications for case updates</div>
            </div>
            <div class="toggle-switch">
              <input checked id="email-notifications" type="checkbox" />
              <span class="toggle-slider"></span>
            </div>
          </div>
          <div class="settings-option">
            <div>
              <div class="option-label">Desktop Notifications</div>
              <div class="option-description">Show desktop notifications for new calls and messages</div>
            </div>
            <div class="toggle-switch">
              <input checked id="desktop-notifications" type="checkbox" />
              <span class="toggle-slider"></span>
            </div>
          </div>
          <div class="settings-option">
            <div>
              <div class="option-label">Sound Alerts</div>
              <div class="option-description">Play sound when new calls or messages arrive</div>
            </div>
            <div class="toggle-switch">
              <input id="sound-alerts" type="checkbox" />
              <span class="toggle-slider"></span>
            </div>
          </div>
        </div>

        <!-- Privacy Settings -->
        <div class="settings-section">
          <div class="settings-section-header">
            <div class="settings-section-title">Privacy & Security</div>
            <div class="settings-section-description">Manage your privacy and security settings</div>
          </div>
          <div class="settings-option">
            <div>
              <div class="option-label">Two-Factor Authentication</div>
              <div class="option-description">Add an extra layer of security to your account</div>
            </div>
            <div class="toggle-switch">
              <input id="two-factor" type="checkbox" />
              <span class="toggle-slider"></span>
            </div>
          </div>
          <div class="settings-option">
            <div>
              <div class="option-label">Session Timeout</div>
              <div class="option-description">Automatically log out after a period of inactivity</div>
            </div>
            <div class="select-wrapper">
              <select class="settings-select" id="session-timeout">
                <option value="15">15 minutes</option>
                <option selected value="30">30 minutes</option>
                <option value="60">1 hour</option>
                <option value="120">2 hours</option>
              </select>
              <div class="select-arrow">
                <svg fill="none" height="6" viewBox="0 0 12 6" width="12" xmlns="http://www.w3.org/2000/svg">
                  <path d="M1 1L6 5L11 1" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" />
                </svg>
              </div>
            </div>
          </div>
          <div class="settings-option">
            <div>
              <div class="option-label">Activity Log</div>
              <div class="option-description">View a log of your account activity</div>
            </div>
            <button class="btn btn-secondary">View Log</button>
          </div>
        </div>

        <!-- Account Settings -->
        <div class="settings-section">
          <div class="settings-section-header">
            <div class="settings-section-title">Account</div>
            <div class="settings-section-description">Manage your account settings</div>
          </div>
          <div class="settings-option">
            <div>
              <div class="option-label">Change Password</div>
              <div class="option-description">Update your account password</div>
            </div>
            <button class="btn btn-secondary" @click="$router.push('/edit-profile')">Change</button>
          </div>
          <div class="settings-option">
            <div>
              <div class="option-label">Edit Profile</div>
              <div class="option-description">Update your profile information</div>
            </div>
            <button class="btn btn-secondary" @click="$router.push('/edit-profile')">Edit</button>
          </div>
          <div class="settings-option">
            <div>
              <div class="option-label">Delete Account</div>
              <div class="option-description">Permanently delete your account and all data</div>
            </div>
            <button class="btn btn-danger">Delete</button>
          </div>
        </div>

        <div class="save-settings">
          <button class="glass-btn filled">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import SidePanel from '../components/SidePanel.vue'

const router = useRouter()

const isSidebarCollapsed = ref(false);
const mobileOpen = ref(false);
const isReading = ref(false);

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
};

const toggleMobileMenu = () => {
  mobileOpen.value = !mobileOpen.value;
};

const mainContentMarginLeft = computed(() => {
  if (window.innerWidth <= 768) {
    return '0px';
  } else if (isSidebarCollapsed.value) {
    return '80px'; // Collapsed sidebar width
  } else {
    return '250px'; // Expanded sidebar width
  }
});

function setBodyFontSizeClass(size) {
  document.body.classList.remove('font-size-small', 'font-size-medium', 'font-size-large');
  document.body.classList.add('font-size-' + size);
}

function setHighContrast(enabled) {
  if (enabled) {
    document.body.classList.add('high-contrast');
    localStorage.setItem('high-contrast', 'true');
  } else {
    document.body.classList.remove('high-contrast');
    localStorage.setItem('high-contrast', 'false');
  }
  // Force update for SPA navigation
  document.body.setAttribute('data-contrast', enabled ? 'high' : 'normal');
}

function readAloud() {
  if (!window.speechSynthesis) return;
  if (isReading.value) {
    window.speechSynthesis.cancel();
    isReading.value = false;
    return;
  }
  const content = document.querySelector('.main-content')?.innerText;
  if (content) {
    window.speechSynthesis.cancel();
    const utterance = new window.SpeechSynthesisUtterance(content);
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.lang = 'en-US';
    utterance.onend = () => { isReading.value = false; };
    utterance.onerror = () => { isReading.value = false; };
    isReading.value = true;
    window.speechSynthesis.speak(utterance);
  }
}

onMounted(() => {
  const sidebar = document.getElementById('sidebar');
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const themeToggle = document.getElementById('theme-toggle');
  const fontSizeSelect = document.getElementById('font-size');
  const highContrastToggle = document.getElementById('high-contrast-toggle');
  const saveSettingsBtn = document.getElementById('save-settings');
  const html = document.documentElement;

  function applyTheme(isDark) {
    html.setAttribute('data-theme', isDark ? 'dark' : 'light');
    if (themeToggle) themeToggle.checked = isDark;
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    // Force update for SPA navigation
    document.body.setAttribute('data-theme', isDark ? 'dark' : 'light');
  }

  function applyFontSize(size) {
    let px = '16px';
    if (size === 'small') px = '14px';
    else if (size === 'large') px = '18px';
    html.style.fontSize = px;
    document.body.style.fontSize = px;
    setBodyFontSizeClass(size);
    if (fontSizeSelect) fontSizeSelect.value = size;
    localStorage.setItem('font-size', size);
  }

  // Apply saved theme
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    applyTheme(savedTheme === 'dark');
  } else {
    applyTheme(true); // Default to dark
  }

  // Apply saved font size
  const savedFontSize = localStorage.getItem('font-size');
  if (savedFontSize) {
    applyFontSize(savedFontSize);
  } else {
    applyFontSize('medium');
  }

  // Apply saved high contrast
  const savedContrast = localStorage.getItem('high-contrast');
  setHighContrast(savedContrast === 'true');
  if (highContrastToggle) highContrastToggle.checked = savedContrast === 'true';

  mobileMenuBtn?.addEventListener('click', () => {
    sidebar?.classList.toggle('mobile-open');
  });

  document.addEventListener('click', (event) => {
    const isMobile = window.innerWidth <= 768;
    if (isMobile && !sidebar?.contains(event.target) && event.target !== mobileMenuBtn) {
      sidebar?.classList.remove('mobile-open');
    }
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
      sidebar?.classList.remove('mobile-open');
    }
  });

  themeToggle?.addEventListener('change', function () {
    const isDark = this.checked;
    applyTheme(isDark);
  });

  fontSizeSelect?.addEventListener('change', function () {
    applyFontSize(this.value);
  });

  highContrastToggle?.addEventListener('change', function () {
    setHighContrast(this.checked);
  });

  saveSettingsBtn?.addEventListener('click', () => {
    // No need to save theme/font-size here, already saved on change
    const settings = {
      theme: themeToggle.checked ? 'dark' : 'light',
      fontSize: fontSizeSelect?.value,
      highContrast: highContrastToggle?.checked,
      emailNotifications: document.getElementById('email-notifications')?.checked,
      desktopNotifications: document.getElementById('desktop-notifications')?.checked,
      soundAlerts: document.getElementById('sound-alerts')?.checked,
      twoFactor: document.getElementById('two-factor')?.checked,
      sessionTimeout: document.getElementById('session-timeout')?.value
    };
    console.log('Settings saved:', settings);
    alert('Settings saved successfully!');
  });

  // Listen for theme/contrast changes (for SPA navigation)
  window.addEventListener('storage', (e) => {
    if (e.key === 'theme') applyTheme(e.newValue === 'dark');
    if (e.key === 'high-contrast') setHighContrast(e.newValue === 'true');
  });
});
</script>

<style scoped>
    :root {
        --base-font-size: 16px;
        /* Dark theme variables */
        --background-color: #0a0a0a;
        --sidebar-bg: #111;
        --content-bg: #222;
        --text-color: #fff;
        --text-secondary: #aaa;
        --border-color: #333;
        --accent-color: #964B00;
        --accent-hover: #b25900;
        --danger-color: #ff3b30;
        --success-color: #4CAF50;
        --pending-color: #FFA500;
        --unassigned-color: #808080;
        --highlight-color: #ff3b30;
        --header-bg: #333;
        --input-bg: #1a1a1a;
    }

    [data-theme="light"] {
        --background-color: #f5f5f5;
        --sidebar-bg: #ffffff;
        --content-bg: #ffffff;
        --text-color: #333;
        --text-secondary: #666;
        --border-color: #ddd;
        --accent-color: #964B00;
        --accent-hover: #b25900;
        --danger-color: #ff3b30;
        --success-color: #4CAF50;
        --pending-color: #FFA500;
        --unassigned-color: #808080;
        --highlight-color: #ff3b30;
        --header-bg: #f0f0f0;
        --input-bg: #f0f0f0;
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Inter', sans-serif;
    }
    
    body {
        background-color: var(--background-color);
        color: var(--text-color);
        display: flex;
        min-height: 100vh;
        transition: background-color 0.3s, color 0.3s;
        font-size: var(--base-font-size);
    }
    
    body.font-size-small {
        font-size: 14px !important;
    }
    
    body.font-size-medium {
        font-size: 16px !important;
    }
    
    body.font-size-large {
        font-size: 18px !important;
    }
    
    body.high-contrast, .high-contrast .main-content, .high-contrast .settings-container, .high-contrast .settings-section, .high-contrast .settings-option {
        background: #000 !important;
        color: #fff !important;
        border-color: #fff !important;
    }
    
    .high-contrast .option-label, .high-contrast .option-description, .high-contrast .settings-section-title, .high-contrast .settings-section-description {
        color: #fff !important;
    }
    
    .high-contrast .btn, .high-contrast .toggle-slider, .high-contrast .settings-select {
        background: #fff !important;
        color: #000 !important;
        border-color: #fff !important;
    }
    
    .settings-wrapper {
        display: flex;
        width: 100%;
        height: 100vh;
        background-color: var(--background-color);
        overflow: hidden;
    }
    
    .mobile-menu-btn {
        display: none;
        position: fixed;
        top: 10px;
        left: 10px;
        background-color: var(--content-bg);
        color: var(--text-color);
        border: 1px solid var(--border-color);
        border-radius: 50%;
        padding: 10px;
        cursor: pointer;
        z-index: 1000;
    }
    
    .sidebar {
        width: 250px;
        flex-shrink: 0;
        background-color: var(--sidebar-bg);
        color: var(--text-color);
        transition: width 0.3s ease, transform 0.3s ease;
        overflow-x: hidden;
        border-radius: 0 30px 30px 0;
        z-index: 100;
        height: 100%;
        display: flex;
        flex-direction: column;
        position: relative;
    }
    
    .sidebar.collapsed {
        width: 80px;
    }
    
    .sidebar-content {
        padding: 30px 0;
        width: 250px;
        height: 100%;
        overflow-y: auto;
    }
    
    .sidebar.collapsed .sidebar-content {
        opacity: 0;
        pointer-events: none;
    }
    
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 30px;
    }
    
    .logo {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        background-color: var(--text-color);
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
    }
    
    .logo img {
        width: 40px;
        height: 40px;
        object-fit: contain;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        padding: 12px 20px;
        cursor: pointer;
        margin-bottom: 5px;
        border-radius: 30px 0 0 30px;
        text-decoration: none;
        color: var(--text-color);
        transition: background-color 0.3s;
    }
    
    .nav-item:hover {
        background-color: rgba(255, 255, 255, 0.05);
    }
    
    .nav-item.active {
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    .nav-icon {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 2px solid var(--text-color);
        margin-right: 15px;
        flex-shrink: 0;
    }
    
    .nav-text {
        font-size: 14px;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .sidebar.collapsed .nav-text {
        display: none;
    }
    
    .user-profile {
        display: flex;
        justify-content: center;
        margin: 30px 0 20px;
    }
    
    .user-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background-color: var(--text-color);
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        overflow: hidden;
    }
    
    .user-avatar svg {
        width: 30px;
        height: 30px;
        fill: var(--background-color);
    }
    
    .status {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
        font-size: 14px;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: green;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .button-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        padding: 0 20px;
    }
    
    .join-queue-btn, .logout-btn {
        width: 100%;
        padding: 10px;
        border-radius: 20px;
        border: none;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
    }
    
    .join-queue-btn {
        background-color: var(--accent-color);
        color: white;
    }
    
    .join-queue-btn:hover {
        background-color: var(--accent-hover);
    }
    
    .logout-btn {
        background-color: #800000; /* Maroon background */
        color: white;
        border: 1px solid #800000; /* Maroon border */
        border-radius: 30px;
        padding: 10px;
        width: 100%;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.3s, border-color 0.3s; /* Add border-color transition */
    }
    
    .logout-btn:hover {
        background-color: var(--danger-color); /* Red background on hover */
        border-color: var(--danger-color); /* Red border on hover */
    }
    
    .main-content {
        flex: 1;
        padding: 20px;
        overflow-y: auto;
        transition: margin-left 0.3s ease;
        font-size: var(--base-font-size);
    }
    
    .sidebar.collapsed ~ .main-content {
        margin-left: 80px;
    }
    
    .header {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        gap: 20px;
    }
    
    .header h1 {
        font-size: 24px;
        font-weight: 600;
        margin: 0 auto 0 0;
    }
    
    .header p {
        font-size: 14px;
        color: var(--text-secondary);
    }
    
    .settings-container {
        background-color: var(--content-bg);
        border-radius: 15px;
        padding: 20px;
        display: flex;
        flex-direction: column;
        gap: 30px;
    }
    
    .settings-section-header {
        margin-bottom: 20px;
    }
    
    .settings-section-title {
        font-size: 18px;
        font-weight: 600;
        color: var(--text-color);
        margin-bottom: 5px;
    }
    
    .settings-section-description {
        font-size: 14px;
        color: var(--text-secondary);
    }
    
    .settings-option {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 0;
        border-bottom: 1px solid var(--border-color);
    }
    
    .settings-option:last-child {
        border-bottom: none;
    }
    
    .option-label {
        font-size: 16px;
        font-weight: 500;
        color: var(--text-color);
    }
    
    .option-description {
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 3px;
    }
    
    .toggle-switch {
        position: relative;
        display: inline-block;
        width: 40px;
        height: 20px;
    }
    
    .toggle-switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }
    
    .toggle-slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: var(--border-color);
        transition: .4s;
        border-radius: 20px;
    }
    
    .toggle-slider:before {
        position: absolute;
        content: "";
        height: 16px;
        width: 16px;
        left: 2px;
        bottom: 2px;
        background-color: var(--content-bg);
        transition: .4s;
        border-radius: 50%;
    }
    
    input:checked + .toggle-slider {
        background-color: var(--accent-color);
    }
    
    input:focus + .toggle-slider {
        box-shadow: 0 0 1px var(--accent-color);
    }
    
    input:checked + .toggle-slider:before {
        transform: translateX(20px);
    }
    
    .select-wrapper {
        position: relative;
        display: inline-block;
    }
    
    .settings-select {
        padding: 8px 25px 8px 10px;
        border-radius: 20px;
        border: 1px solid var(--border-color);
        background-color: var(--content-bg);
        color: var(--text-color);
        font-size: 14px;
        cursor: pointer;
        outline: none;
        -webkit-appearance: none;
        -moz-appearance: none;
        appearance: none;
    }
    
    .select-arrow {
        position: absolute;
        top: 50%;
        right: 10px;
        transform: translateY(-50%);
        pointer-events: none;
        color: var(--text-secondary);
    }
    
    .select-arrow svg {
        width: 12px;
        height: 6px;
    }
    
    .btn {
        padding: 8px 15px;
        border-radius: 20px;
        border: none;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
    }
    
    .btn-primary {
        background-color: var(--accent-color);
        color: white;
    }
    
    .btn-secondary {
        background-color: var(--content-bg);
        color: var(--text-color);
        border: 1px solid var(--border-color);
    }
    
    .btn-danger {
        background-color: #8B0000;
        color: white;
    }
    
    .btn-danger:hover {
        background-color: #8B0000;
    }
    
    .save-settings {
        margin-top: 20px;
        text-align: right;
    }
    
    /* Responsive styles */
    @media (max-width: 768px) {
        .settings-wrapper {
            flex-direction: column;
        }
        
        .mobile-menu-btn {
            display: block;
        }
        
        .sidebar {
            position: fixed;
            top: 0;
            left: -250px;
            height: 100vh;
            z-index: 1000;
            transition: transform 0.3s ease;
        }
        
        .sidebar.collapsed {
            transform: translateX(0);
            left: -250px;
        }
        
        .sidebar.mobile-open {
            transform: translateX(250px);
            left: 0;
        }
        
        .main-content {
            flex: 1;
            padding: 10px;
            overflow-y: auto;
            margin-left: 0 !important; /* Override desktop margin */
        }
        
        .header {
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
        }
        
        .header h1 {
            font-size: 20px;
        }
        
        .header p {
            font-size: 12px;
        }
        
        .settings-container {
            padding: 15px;
            gap: 20px;
        }
        
        .settings-option {
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
            padding: 10px 0;
        }
        
        .toggle-switch, .select-wrapper, .btn {
            align-self: flex-end;
        }
    }
    
    @media (min-width: 769px) {
        .mobile-menu-btn {
            display: none;
        }
        
        .sidebar {
            width: 250px;
            transition: width 0.3s ease;
            transform: translateX(0);
            left: 0;
        }
        
        .sidebar.collapsed {
            width: 80px;
        }
        
        .sidebar.mobile-open { /* This class is for mobile, hide on desktop */
            transform: translateX(0);
            left: 0;
        }
        
        .main-content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
    }
    
    /* Added new sidebar-toggle styles */
    .sidebar-toggle {
        background-color: transparent; /* Make background transparent */
        color: var(--text-color);
        border: none; /* Remove border */
        border-radius: 30px;
        padding: 8px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background-color 0.3s;
        margin-right: 20px; /* Add some space between the toggle and the title */
    }
    
    .sidebar-toggle:hover {
        background-color: rgba(150, 75, 0, 0.1); /* Subtle hover effect using accent color with transparency */
    }
    
    .sidebar-toggle svg {
        width: 20px;
        height: 20px;
    }

    /* Add expand button styles */
    .expand-btn {
        position: fixed;
        top: 50px;
        left: 5px;
    }

    /* Remove old toggle button styles */
    .toggle-btn {
        position: absolute;
        top: 50px;
        right: -15px;
        width: 30px;
        height: 30px;
        background-color: var(--text-color);
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        z-index: 10;
        border: 1px solid var(--border-color);
        color: var(--background-color);
        font-weight: bold;
        font-size: 14px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }

    .main-content, .settings-container, .settings-card, .status-badge, .view-tab, .settings-table {
        background: var(--content-bg);
        color: var(--text-color);
        border-color: var(--border-color);
    }

    .status-badge, .view-tab.active {
        background: var(--accent-color) !important;
        color: #fff !important;
        border-color: var(--accent-color) !important;
    }
</style>