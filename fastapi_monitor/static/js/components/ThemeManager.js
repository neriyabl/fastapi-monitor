/**
 * Advanced ThemeManager - Handles Light/Dark mode + Color schemes
 * Architecture: Strategy + Observer patterns for maximum flexibility
 */
class ThemeManager extends EventEmitter {
  constructor(options = {}) {
    super();

    this.config = {
      defaultMode: options.defaultMode || "light",
      defaultScheme: options.defaultScheme || "default",
      storageKey: options.storageKey || "fastapi-monitor-theme",
      respectSystemPreference: options.respectSystemPreference !== false,
      ...options,
    };

    // Available color schemes
    this.schemes = new Map([
      [
        "default",
        {
          name: "Default",
          description: "Clean & Professional",
          category: "neutral",
        },
      ],
      [
        "ocean",
        {
          name: "Ocean",
          description: "Calm & Professional",
          category: "cool",
        },
      ],
      [
        "forest",
        {
          name: "Forest",
          description: "Natural & Calming",
          category: "nature",
        },
      ],
      [
        "sunset",
        {
          name: "Sunset",
          description: "Warm & Energetic",
          category: "warm",
        },
      ],
      [
        "purple",
        {
          name: "Purple",
          description: "Creative & Modern",
          category: "vibrant",
        },
      ],
    ]);

    // Current theme state
    this.state = {
      mode: this.config.defaultMode,
      scheme: this.config.defaultScheme,
      systemPreference: this.getSystemPreference(),
      isInitialized: false,
    };

    this.init();
  }

  /**
   * Initialize theme manager
   */
  async init() {
    try {
      // Load saved preferences
      await this.loadSavedTheme();

      // Apply initial theme
      this.applyTheme();

      // Setup system preference listener
      if (this.config.respectSystemPreference) {
        this.setupSystemListener();
      }

      this.state.isInitialized = true;
      this.emit("theme:initialized", this.getThemeState());
    } catch (error) {
      console.error("Failed to initialize theme manager:", error);
      this.applyFallbackTheme();
    }
  }

  /**
   * Get system color scheme preference
   * @returns {string} 'light' or 'dark'
   */
  getSystemPreference() {
    if (!window.matchMedia) return "light";
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  /**
   * Load saved theme from storage
   */
  async loadSavedTheme() {
    try {
      const saved = localStorage.getItem(this.config.storageKey);
      if (saved) {
        const { mode, scheme } = JSON.parse(saved);

        if (this.isValidMode(mode) && this.isValidScheme(scheme)) {
          this.state.mode = mode;
          this.state.scheme = scheme;
          return;
        }
      }
    } catch (error) {
      console.warn("Failed to load saved theme:", error);
    }

    // Fallback to system preference if enabled
    if (this.config.respectSystemPreference) {
      this.state.mode = this.getSystemPreference();
    }
  }

  /**
   * Apply current theme to document
   */
  applyTheme() {
    const { mode, scheme } = this.state;

    // Validate theme combination
    if (!this.isValidMode(mode) || !this.isValidScheme(scheme)) {
      console.warn(`Invalid theme combination: ${mode}/${scheme}`);
      this.applyFallbackTheme();
      return;
    }

    // Apply theme attributes with smooth transition
    this.addTransition();

    requestAnimationFrame(() => {
      document.documentElement.setAttribute("data-theme", mode);
      document.documentElement.setAttribute("data-scheme", scheme);

      // Remove transition after animation
      setTimeout(() => this.removeTransition(), 300);
    });

    // Save to storage
    this.saveTheme();

    // Emit change event
    this.emit("theme:changed", this.getThemeState());
  }

  /**
   * Apply fallback theme in case of errors
   */
  applyFallbackTheme() {
    this.state.mode = "light";
    this.state.scheme = "default";
    this.applyTheme();
  }

  /**
   * Add smooth transition for theme changes
   */
  addTransition() {
    const style = document.createElement("style");
    style.id = "theme-transition";
    style.textContent = `
      *, *::before, *::after {
        transition:
          background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1),
          color 0.3s cubic-bezier(0.4, 0, 0.2, 1),
          border-color 0.3s cubic-bezier(0.4, 0, 0.2, 1),
          box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
      }
    `;
    document.head.appendChild(style);
  }

  /**
   * Remove transition styles
   */
  removeTransition() {
    const style = document.getElementById("theme-transition");
    if (style) {
      style.remove();
    }
  }

  /**
   * Save current theme to storage
   */
  saveTheme() {
    try {
      const themeData = {
        mode: this.state.mode,
        scheme: this.state.scheme,
        timestamp: Date.now(),
      };
      localStorage.setItem(this.config.storageKey, JSON.stringify(themeData));
    } catch (error) {
      console.warn("Failed to save theme:", error);
    }
  }

  /**
   * Setup system preference change listener
   */
  setupSystemListener() {
    if (!window.matchMedia) return;

    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const handleSystemChange = (e) => {
      const newPreference = e.matches ? "dark" : "light";
      this.state.systemPreference = newPreference;

      this.emit("system:changed", { preference: newPreference });

      // Auto-switch only if user hasn't manually set a preference
      if (this.config.respectSystemPreference && !this.hasManualPreference()) {
        this.setMode(newPreference);
      }
    };

    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener("change", handleSystemChange);
    } else {
      // Legacy browsers
      mediaQuery.addListener(handleSystemChange);
    }
  }

  /**
   * Check if user has manually set a theme preference
   * @returns {boolean}
   */
  hasManualPreference() {
    try {
      const saved = localStorage.getItem(this.config.storageKey);
      return !!saved;
    } catch {
      return false;
    }
  }

  /**
   * Set theme mode (light/dark)
   * @param {string} mode - Theme mode
   */
  setMode(mode) {
    if (!this.isValidMode(mode)) {
      console.warn(`Invalid theme mode: ${mode}`);
      return;
    }

    if (this.state.mode !== mode) {
      this.state.mode = mode;
      this.applyTheme();
      this.emit("mode:changed", { mode, scheme: this.state.scheme });
    }
  }

  /**
   * Set color scheme
   * @param {string} scheme - Color scheme
   */
  setScheme(scheme) {
    if (!this.isValidScheme(scheme)) {
      console.warn(`Invalid color scheme: ${scheme}`);
      return;
    }

    if (this.state.scheme !== scheme) {
      this.state.scheme = scheme;
      this.applyTheme();
      this.emit("scheme:changed", { mode: this.state.mode, scheme });
    }
  }

  /**
   * Set both mode and scheme
   * @param {string} mode - Theme mode
   * @param {string} scheme - Color scheme
   */
  setTheme(mode, scheme) {
    if (!this.isValidMode(mode) || !this.isValidScheme(scheme)) {
      console.warn(`Invalid theme combination: ${mode}/${scheme}`);
      return;
    }

    const changed = this.state.mode !== mode || this.state.scheme !== scheme;

    if (changed) {
      this.state.mode = mode;
      this.state.scheme = scheme;
      this.applyTheme();
    }
  }

  /**
   * Toggle between light and dark mode
   */
  toggleMode() {
    const newMode = this.state.mode === "light" ? "dark" : "light";
    this.setMode(newMode);
  }

  /**
   * Cycle to next color scheme
   */
  nextScheme() {
    const schemes = Array.from(this.schemes.keys());
    const currentIndex = schemes.indexOf(this.state.scheme);
    const nextIndex = (currentIndex + 1) % schemes.length;
    this.setScheme(schemes[nextIndex]);
  }

  /**
   * Cycle to previous color scheme
   */
  previousScheme() {
    const schemes = Array.from(this.schemes.keys());
    const currentIndex = schemes.indexOf(this.state.scheme);
    const prevIndex =
      currentIndex === 0 ? schemes.length - 1 : currentIndex - 1;
    this.setScheme(schemes[prevIndex]);
  }

  /**
   * Validate theme mode
   * @param {string} mode - Mode to validate
   * @returns {boolean}
   */
  isValidMode(mode) {
    return ["light", "dark"].includes(mode);
  }

  /**
   * Validate color scheme
   * @param {string} scheme - Scheme to validate
   * @returns {boolean}
   */
  isValidScheme(scheme) {
    return this.schemes.has(scheme);
  }

  /**
   * Get current theme state
   * @returns {Object}
   */
  getThemeState() {
    return {
      ...this.state,
      schemeData: this.schemes.get(this.state.scheme),
      combinations: this.getAvailableCombinations(),
    };
  }

  /**
   * Get all available theme combinations
   * @returns {Array}
   */
  getAvailableCombinations() {
    const modes = ["light", "dark"];
    const schemes = Array.from(this.schemes.keys());

    return modes.flatMap((mode) =>
      schemes.map((scheme) => ({
        mode,
        scheme,
        name: `${this.schemes.get(scheme).name} ${
          mode === "light" ? "Light" : "Dark"
        }`,
        description: this.schemes.get(scheme).description,
        category: this.schemes.get(scheme).category,
        preview: `theme-preview--${mode}-${scheme}`,
      })),
    );
  }

  /**
   * Get schemes by category
   * @param {string} category - Category to filter by
   * @returns {Array}
   */
  getSchemesByCategory(category) {
    return Array.from(this.schemes.entries())
      .filter(([, data]) => data.category === category)
      .map(([key, data]) => ({ key, ...data }));
  }

  /**
   * Register a new color scheme
   * @param {string} key - Scheme key
   * @param {Object} data - Scheme data
   */
  registerScheme(key, data) {
    this.schemes.set(key, {
      name: data.name,
      description: data.description || "",
      category: data.category || "custom",
      ...data,
    });

    this.emit("scheme:registered", { key, data });
  }

  /**
   * Export current theme settings
   * @returns {Object}
   */
  exportSettings() {
    return {
      mode: this.state.mode,
      scheme: this.state.scheme,
      systemPreference: this.state.systemPreference,
      availableSchemes: Array.from(this.schemes.keys()),
      timestamp: Date.now(),
      version: "2.0",
    };
  }

  /**
   * Import theme settings
   * @param {Object} settings - Settings to import
   */
  importSettings(settings) {
    if (settings.version === "2.0") {
      if (settings.mode && settings.scheme) {
        this.setTheme(settings.mode, settings.scheme);
      }
    }
  }

  /**
   * Reset to default theme
   */
  reset() {
    this.state.mode = this.config.defaultMode;
    this.state.scheme = this.config.defaultScheme;
    this.applyTheme();
    this.emit("theme:reset", this.getThemeState());
  }

  /**
   * Cleanup resources
   */
  destroy() {
    this.clear(); // Clear all event listeners
    this.removeTransition();
    this.emit("theme:destroyed");
  }
}

// Export for module systems or global use
if (typeof module !== "undefined" && module.exports) {
  module.exports = ThemeManager;
} else {
  window.ThemeManager = ThemeManager;
}
