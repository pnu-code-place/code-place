/**
 * Queue to store pending toast messages
 * This queue is used to prevent multiple toasts from being displayed at the same time
 * @type {Array<{message: string, type: string, duration: number}>}
 */
const toastQueue = [];

// Flag to track if a toast is currently being displayed
let isShowingToast = false;

/**
 * Creates the DOM element for a toast notification
 * @param {string} message - The message to display in the toast
 * @param {string} type - The type of toast (info, success, error, etc.)
 * @returns {HTMLElement} The created toast element
 */
const createToastElement = (message, type) => {
  const toast = document.createElement("div");
  toast.className = `code-place-hub-toast ${type}`;

  toast.innerHTML = `
    <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: center;">
      <img src="${chrome.runtime.getURL(
        "assets/thumbnail.png"
      )}" width="14" height="14" style="margin-right: 8px;">
      <span style="font-weight: 500; font-size: 14px;">Code Place Hub</span>
    </div>
    <div style="text-align: center; font-size: 12px;">${message}</div>
  `;

  return toast;
};

/**
 * Applies styling to the toast element
 * @param {HTMLElement} toast - The toast element to style
 */
const styleToastElement = (toast) => {
  Object.assign(toast.style, {
    position: "fixed",
    top: "20px",
    left: "50%",
    transform: "translateX(-50%)",
    padding: "12px 20px",
    borderRadius: "6px",
    backgroundColor: "#FFFFFF",
    color: "#000000",
    zIndex: "10000",
    opacity: "0",
    transition: "opacity 0.3s ease-in",
    boxShadow: "0 3px 10px rgba(0, 0, 0, 0.16)",
    border: "1px solid #f0f0f0",
  });
};

/**
 * Processes the next toast in queue if available
 */
const processNextToast = () => {
  if (toastQueue.length > 0) {
    const nextToast = toastQueue.shift();
    showToast(nextToast.message, nextToast.type, nextToast.duration);
  }
};

/**
 * Shows a toast notification with the specified message, type and duration
 * @param {string} message - The message to display in the toast
 * @param {string} [type='info'] - The type of toast (info, success, error, etc.)
 * @param {number} [duration=2000] - How long the toast should be displayed in milliseconds
 */
const showToast = (message, type = "info", duration = 2000) => {
  if (isShowingToast) {
    toastQueue.push({ message, type, duration });
    return;
  }

  isShowingToast = true;

  const toast = createToastElement(message, type);
  styleToastElement(toast);
  document.body.appendChild(toast);

  // Fade in animation
  setTimeout(() => {
    toast.style.opacity = "1";
  }, 10);

  // Fade out after duration
  setTimeout(() => {
    toast.style.opacity = "0";

    // Remove from DOM after transition completes
    setTimeout(() => {
      document.body.removeChild(toast);
      isShowingToast = false;
      processNextToast();
    }, 300);
  }, duration);
};
