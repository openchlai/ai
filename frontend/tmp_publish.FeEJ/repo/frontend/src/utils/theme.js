export function applyTheme() {
  const root = document.documentElement;
    root.style.setProperty('--background-color', '#f5f5f5');
    root.style.setProperty('--sidebar-bg', '#ffffff');
    root.style.setProperty('--content-bg', '#ffffff');
    root.style.setProperty('--text-color', '#222');
    root.style.setProperty('--text-secondary', '#666');
    root.style.setProperty('--border-color', '#ddd');
    root.style.setProperty('--card-bg', '#fff');
    root.style.setProperty('--logo-bg', '#fff');
    root.style.setProperty('--logo-color', '#222');
    root.style.setProperty('--header-bg', '#f0f0f0');
    root.style.setProperty('--input-bg', '#fff');
    root.setAttribute('data-theme', 'light');
  // Accent and status colors
  root.style.setProperty('--accent-color', '#8B4513');
  root.style.setProperty('--accent-hover', '#A0522D');
  root.style.setProperty('--danger-color', '#ff3b30');
  root.style.setProperty('--success-color', '#4CAF50');
  root.style.setProperty('--pending-color', '#FFA500');
  root.style.setProperty('--unassigned-color', '#808080');
  root.style.setProperty('--highlight-color', '#ff3b30');
  root.style.setProperty('--critical-color', '#ff3b30');
  root.style.setProperty('--high-color', '#ff9500');
  root.style.setProperty('--medium-color', '#007aff');
  root.style.setProperty('--low-color', '#34c759');
}

export function getCurrentTheme() {
  return 'light';
}