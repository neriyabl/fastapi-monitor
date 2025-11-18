/**
 * DashboardController - Main application controller
 * Implements MVC pattern with clean separation of concerns
 */
class DashboardController extends EventEmitter {
  constructor(options = {}) {
    super();

    this.config = {
      refreshInterval: options.refreshInterval || 5000,
      autoRefresh: options.autoRefresh !== false,
      apiEndpoints: {
        stats: "/api/stats",
        requests: "/api/requests",
        analytics: "/api/analytics",
        ...options.apiEndpoints,
      },
      ...options,
    };

    this.state = {
      isLoading: false,
      lastUpdate: null,
      error: null,
      stats: null,
      requests: [],
      autoRefreshEnabled: this.config.autoRefresh,
    };

    this.refreshTimer = null;
    this.abortController = null;

    this.init();
  }

  /**
   * Initialize dashboard
   */
  async init() {
    try {
      this.emit("dashboard:initializing");

      // Load initial data
      await this.loadInitialData();

      // Setup auto-refresh if enabled
      if (this.state.autoRefreshEnabled) {
        this.startAutoRefresh();
      }

      // Setup event listeners
      this.setupEventListeners();

      this.emit("dashboard:initialized", { state: this.state });
    } catch (error) {
      this.handleError("Failed to initialize dashboard", error);
    }
  }

  /**
   * Load initial dashboard data
   */
  async loadInitialData() {
    this.setLoading(true);

    try {
      const [stats, requests] = await Promise.all([
        this.fetchStats(),
        this.fetchRequests(),
      ]);

      this.updateState({
        stats,
        requests,
        lastUpdate: new Date(),
        error: null,
      });

      this.emit("data:loaded", { stats, requests });
    } catch (error) {
      this.handleError("Failed to load initial data", error);
    } finally {
      this.setLoading(false);
    }
  }

  /**
   * Fetch statistics from API
   * @returns {Promise<Object>} Stats data
   */
  async fetchStats() {
    const response = await this.apiRequest(this.config.apiEndpoints.stats);
    return response;
  }

  /**
   * Fetch requests from API
   * @param {Object} params - Query parameters
   * @returns {Promise<Array>} Requests data
   */
  async fetchRequests(params = {}) {
    const url = new URL(
      this.config.apiEndpoints.requests,
      window.location.origin,
    );
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });

    const response = await this.apiRequest(url.toString());
    return response;
  }

  /**
   * Fetch analytics data
   * @param {string} resolution - Time resolution
   * @returns {Promise<Object>} Analytics data
   */
  async fetchAnalytics(resolution = "30s") {
    const url = new URL(
      this.config.apiEndpoints.analytics,
      window.location.origin,
    );
    url.searchParams.append("resolution", resolution);

    const response = await this.apiRequest(url.toString());
    return response;
  }

  /**
   * Generic API request handler with error handling and cancellation
   * @param {string} url - Request URL
   * @param {Object} options - Fetch options
   * @returns {Promise<*>} Response data
   */
  async apiRequest(url, options = {}) {
    // Cancel previous request if still pending
    if (this.abortController) {
      this.abortController.abort();
    }

    this.abortController = new AbortController();

    const defaultOptions = {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      signal: this.abortController.signal,
      ...options,
    };

    try {
      const response = await fetch(url, defaultOptions);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      if (error.name === "AbortError") {
        console.log("Request cancelled");
        return null;
      }
      throw error;
    }
  }

  /**
   * Refresh dashboard data
   */
  async refresh() {
    if (this.state.isLoading) return;

    this.emit("dashboard:refreshing");

    try {
      await this.loadInitialData();
      this.emit("dashboard:refreshed");
    } catch (error) {
      this.handleError("Failed to refresh data", error);
    }
  }

  /**
   * Start auto-refresh timer
   */
  startAutoRefresh() {
    this.stopAutoRefresh();

    this.refreshTimer = setInterval(() => {
      if (!document.hidden && this.state.autoRefreshEnabled) {
        this.refresh();
      }
    }, this.config.refreshInterval);

    this.updateState({ autoRefreshEnabled: true });
    this.emit("autorefresh:started");
  }

  /**
   * Stop auto-refresh timer
   */
  stopAutoRefresh() {
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }

    this.updateState({ autoRefreshEnabled: false });
    this.emit("autorefresh:stopped");
  }

  /**
   * Toggle auto-refresh
   */
  toggleAutoRefresh() {
    if (this.state.autoRefreshEnabled) {
      this.stopAutoRefresh();
    } else {
      this.startAutoRefresh();
    }
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Pause auto-refresh when page is hidden
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        this.emit("dashboard:paused");
      } else {
        this.emit("dashboard:resumed");
        // Refresh data when page becomes visible again
        if (this.state.autoRefreshEnabled) {
          this.refresh();
        }
      }
    });

    // Handle online/offline status
    window.addEventListener("online", () => {
      this.emit("connection:online");
      if (this.state.autoRefreshEnabled) {
        this.refresh();
      }
    });

    window.addEventListener("offline", () => {
      this.emit("connection:offline");
      this.stopAutoRefresh();
    });
  }

  /**
   * Update internal state
   * @param {Object} updates - State updates
   */
  updateState(updates) {
    const previousState = { ...this.state };
    this.state = { ...this.state, ...updates };
    this.emit("state:updated", {
      previous: previousState,
      current: this.state,
      changes: updates,
    });
  }

  /**
   * Set loading state
   * @param {boolean} isLoading - Loading state
   */
  setLoading(isLoading) {
    this.updateState({ isLoading });
    this.emit(isLoading ? "loading:start" : "loading:end");
  }

  /**
   * Handle errors consistently
   * @param {string} message - Error message
   * @param {Error} error - Error object
   */
  handleError(message, error) {
    console.error(message, error);

    const errorInfo = {
      message,
      error: error.message,
      timestamp: new Date(),
      stack: error.stack,
    };

    this.updateState({ error: errorInfo });
    this.emit("error", errorInfo);
  }

  /**
   * Get current state
   * @returns {Object} Current state
   */
  getState() {
    return { ...this.state };
  }

  /**
   * Get configuration
   * @returns {Object} Current configuration
   */
  getConfig() {
    return { ...this.config };
  }

  /**
   * Update configuration
   * @param {Object} updates - Configuration updates
   */
  updateConfig(updates) {
    this.config = { ...this.config, ...updates };
    this.emit("config:updated", { config: this.config });
  }

  /**
   * Cleanup resources
   */
  destroy() {
    this.stopAutoRefresh();

    if (this.abortController) {
      this.abortController.abort();
    }

    this.clear(); // Clear all event listeners
    this.emit("dashboard:destroyed");
  }
}

// Export for module systems or global use
if (typeof module !== "undefined" && module.exports) {
  module.exports = DashboardController;
} else {
  window.DashboardController = DashboardController;
}
