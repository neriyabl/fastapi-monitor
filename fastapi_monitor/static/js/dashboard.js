/**
 * Dashboard Application - Main entry point
 * Clean architecture with separation of concerns
 */
class DashboardApp {
  constructor() {
    this.components = new Map();
    this.state = {
      isInitialized: false,
      isLoading: false,
    };

    this.init();
  }

  /**
   * Initialize the dashboard application
   */
  async init() {
    try {
      // Initialize core components
      await this.initializeComponents();

      // Setup event listeners
      this.setupEventListeners();

      // Load initial data
      await this.loadInitialData();

      this.state.isInitialized = true;
      console.log("✅ Dashboard initialized successfully");
    } catch (error) {
      console.error("❌ Failed to initialize dashboard:", error);
      this.showError("Failed to initialize dashboard");
    }
  }

  /**
   * Initialize all dashboard components
   */
  async initializeComponents() {
    // Initialize Theme Manager
    this.components.set(
      "theme",
      new ThemeManager({
        defaultMode: document.body.dataset.theme || "light",
        defaultScheme: document.body.dataset.scheme || "default",
      }),
    );

    // Initialize Dashboard Controller
    this.components.set(
      "dashboard",
      new DashboardController({
        refreshInterval: 5000,
        autoRefresh: true,
      }),
    );

    // Setup component communication
    this.setupComponentCommunication();
  }

  /**
   * Setup communication between components
   */
  setupComponentCommunication() {
    const theme = this.components.get("theme");
    const dashboard = this.components.get("dashboard");

    // Theme change events
    theme.on("theme:changed", (data) => {
      console.log("🎨 Theme changed:", data);
      this.updateThemeUI(data);
    });

    // Dashboard events
    dashboard.on("loading:start", () => this.showLoading());
    dashboard.on("loading:end", () => this.hideLoading());
    dashboard.on("data:loaded", (data) => this.updateUI(data));
    dashboard.on("error", (error) => this.showError(error.message));
  }

  /**
   * Setup DOM event listeners
   */
  setupEventListeners() {
    // Refresh button
    const refreshBtn = document.getElementById("refresh-btn");
    if (refreshBtn) {
      refreshBtn.addEventListener("click", () => {
        this.components.get("dashboard").refresh();
      });
    }

    // Auto-refresh toggle
    const autoRefreshToggle = document.getElementById("auto-refresh-toggle");
    if (autoRefreshToggle) {
      autoRefreshToggle.addEventListener("change", (e) => {
        if (e.target.checked) {
          this.components.get("dashboard").startAutoRefresh();
        } else {
          this.components.get("dashboard").stopAutoRefresh();
        }
      });
    }

    // Theme selector
    this.setupThemeSelector();
  }

  /**
   * Setup theme selector UI
   */
  setupThemeSelector() {
    const themeSelector = document.getElementById("theme-selector");
    const themeButton = themeSelector?.querySelector(".theme-selector__button");
    const themeDropdown = document.getElementById("theme-dropdown");

    if (!themeSelector || !themeButton || !themeDropdown) return;

    // Populate theme options
    this.populateThemeOptions(themeDropdown);

    // Toggle dropdown
    themeButton.addEventListener("click", (e) => {
      e.stopPropagation();
      themeDropdown.classList.toggle("is-open");
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", () => {
      themeDropdown.classList.remove("is-open");
    });

    // Prevent dropdown close when clicking inside
    themeDropdown.addEventListener("click", (e) => {
      e.stopPropagation();
    });
  }

  /**
   * Populate theme selector options
   */
  populateThemeOptions(dropdown) {
    const theme = this.components.get("theme");
    const combinations = theme.getAvailableCombinations();
    const currentState = theme.getThemeState();

    dropdown.innerHTML = combinations
      .map(
        (combo) => `
      <button
        class="theme-selector__option ${
          combo.mode === currentState.mode &&
          combo.scheme === currentState.scheme
            ? "is-active"
            : ""
        }"
        data-mode="${combo.mode}"
        data-scheme="${combo.scheme}"
      >
        <div class="theme-preview ${combo.preview}"></div>
        <div>
          <div class="font-medium">${combo.name}</div>
          <div class="text-xs text-secondary">${combo.description}</div>
        </div>
      </button>
    `,
      )
      .join("");

    // Add event listeners to theme options
    dropdown.querySelectorAll(".theme-selector__option").forEach((option) => {
      option.addEventListener("click", () => {
        const mode = option.dataset.mode;
        const scheme = option.dataset.scheme;
        theme.setTheme(mode, scheme);
        dropdown.classList.remove("is-open");
      });
    });
  }

  /**
   * Load initial dashboard data
   */
  async loadInitialData() {
    const dashboard = this.components.get("dashboard");
    await dashboard.loadInitialData();
  }

  /**
   * Update UI with new data
   */
  updateUI(data) {
    this.updateStatsUI(data.stats);
    this.updateRequestsUI(data.requests);
  }

  /**
   * Update statistics UI
   */
  updateStatsUI(stats) {
    const container = document.getElementById("stats-container");
    if (!container || !stats) return;

    const statsCards = [
      {
        icon: "📊",
        value: stats.total_requests?.toLocaleString() || "0",
        label: "Total Requests",
        color: "primary",
      },
      {
        icon: "⚡",
        value: `${stats.avg_response_time || 0}ms`,
        label: "Avg Response Time",
        color: "success",
      },
      {
        icon: "❌",
        value: stats.error_count?.toLocaleString() || "0",
        label: "Errors",
        color: "error",
      },
      {
        icon: "✅",
        value: this.calculateSuccessRate(stats),
        label: "Success Rate",
        color: "info",
      },
    ];

    container.innerHTML = statsCards
      .map(
        (card) => `
      <div class="stat-card fade-in">
        <div class="stat-card__icon">${card.icon}</div>
        <div class="stat-card__value">${card.value}</div>
        <div class="stat-card__label">${card.label}</div>
      </div>
    `,
      )
      .join("");
  }

  /**
   * Update requests table UI
   */
  updateRequestsUI(requests) {
    const container = document.getElementById("requests-table-container");
    if (!container || !requests) return;

    if (requests.length === 0) {
      container.innerHTML = `
        <div class="text-center text-muted py-8">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" class="mx-auto mb-4 opacity-50">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          <p>No requests yet</p>
        </div>
      `;
      return;
    }

    const tableHTML = `
      <table class="table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Method</th>
            <th>Path</th>
            <th>Status</th>
            <th>Response Time</th>
            <th>Size</th>
            <th>IP</th>
          </tr>
        </thead>
        <tbody>
          ${requests
            .map(
              (req) => `
            <tr class="hover-lift transition-all">
              <td class="font-mono text-sm">${req.formatted_time || "N/A"}</td>
              <td>
                <span class="badge method-${
                  req.method?.toLowerCase() || "unknown"
                }">${req.method || "N/A"}</span>
              </td>
              <td class="font-mono text-sm truncate" style="max-width: 200px;" title="${
                req.path || "N/A"
              }">
                ${req.path || "N/A"}
              </td>
              <td>
                <span class="badge status-${Math.floor(
                  (req.status_code || 0) / 100,
                )}00">
                  ${req.status_code || "N/A"}
                </span>
              </td>
              <td class="font-mono text-sm">${
                req.response_time ? `${req.response_time.toFixed(1)}ms` : "N/A"
              }</td>
              <td class="text-sm">${this.formatBytes(
                req.response_size || 0,
              )}</td>
              <td class="font-mono text-xs text-muted">${
                req.client_ip || "N/A"
              }</td>
            </tr>
          `,
            )
            .join("")}
        </tbody>
      </table>
    `;

    container.innerHTML = tableHTML;
  }

  /**
   * Update theme UI elements
   */
  updateThemeUI(themeData) {
    // Update theme selector dropdown
    const dropdown = document.getElementById("theme-dropdown");
    if (dropdown) {
      this.populateThemeOptions(dropdown);
    }
  }

  /**
   * Calculate success rate from stats
   */
  calculateSuccessRate(stats) {
    if (!stats.status_codes || stats.total_requests === 0) return "0%";

    const successCodes = ["200", "201", "202", "204"];
    const successCount = successCodes.reduce((sum, code) => {
      return sum + (stats.status_codes[code] || 0);
    }, 0);

    const rate = (successCount / stats.total_requests) * 100;
    return `${rate.toFixed(1)}%`;
  }

  /**
   * Format bytes to human readable format
   */
  formatBytes(bytes) {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  }

  /**
   * Show loading state
   */
  showLoading() {
    this.state.isLoading = true;
    const overlay = document.getElementById("loading-overlay");
    if (overlay) {
      overlay.style.display = "flex";
    }
  }

  /**
   * Hide loading state
   */
  hideLoading() {
    this.state.isLoading = false;
    const overlay = document.getElementById("loading-overlay");
    if (overlay) {
      overlay.style.display = "none";
    }
  }

  /**
   * Show error message
   */
  showError(message) {
    console.error("Dashboard Error:", message);
    // You could implement a toast notification system here
  }

  /**
   * Get component instance
   */
  getComponent(name) {
    return this.components.get(name);
  }

  /**
   * Cleanup resources
   */
  destroy() {
    this.components.forEach((component) => {
      if (component.destroy) {
        component.destroy();
      }
    });
    this.components.clear();
  }
}

// Initialize dashboard when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    window.dashboardApp = new DashboardApp();
  });
} else {
  window.dashboardApp = new DashboardApp();
}

// Export for debugging
window.DashboardApp = DashboardApp;
