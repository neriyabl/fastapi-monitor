/**
 * EventEmitter - Lightweight event system for component communication
 * Follows the Observer pattern for loose coupling
 */
class EventEmitter {
  constructor() {
    this.events = new Map();
  }

  /**
   * Subscribe to an event
   * @param {string} event - Event name
   * @param {Function} callback - Event handler
   * @param {Object} options - Options (once, priority)
   */
  on(event, callback, options = {}) {
    if (!this.events.has(event)) {
      this.events.set(event, []);
    }

    const listener = {
      callback,
      once: options.once || false,
      priority: options.priority || 0,
    };

    const listeners = this.events.get(event);
    listeners.push(listener);

    // Sort by priority (higher first)
    listeners.sort((a, b) => b.priority - a.priority);

    return () => this.off(event, callback);
  }

  /**
   * Subscribe to an event once
   * @param {string} event - Event name
   * @param {Function} callback - Event handler
   */
  once(event, callback) {
    return this.on(event, callback, { once: true });
  }

  /**
   * Unsubscribe from an event
   * @param {string} event - Event name
   * @param {Function} callback - Event handler to remove
   */
  off(event, callback) {
    if (!this.events.has(event)) return;

    const listeners = this.events.get(event);
    const index = listeners.findIndex(
      (listener) => listener.callback === callback,
    );

    if (index > -1) {
      listeners.splice(index, 1);
    }

    if (listeners.length === 0) {
      this.events.delete(event);
    }
  }

  /**
   * Emit an event
   * @param {string} event - Event name
   * @param {*} data - Event data
   */
  emit(event, data) {
    if (!this.events.has(event)) return;

    const listeners = this.events.get(event);
    const toRemove = [];

    listeners.forEach((listener, index) => {
      try {
        listener.callback(data);
        if (listener.once) {
          toRemove.push(index);
        }
      } catch (error) {
        console.error(`Error in event listener for "${event}":`, error);
      }
    });

    // Remove one-time listeners
    toRemove.reverse().forEach((index) => listeners.splice(index, 1));
  }

  /**
   * Remove all listeners for an event or all events
   * @param {string} [event] - Specific event to clear
   */
  clear(event) {
    if (event) {
      this.events.delete(event);
    } else {
      this.events.clear();
    }
  }

  /**
   * Get listener count for an event
   * @param {string} event - Event name
   * @returns {number} Number of listeners
   */
  listenerCount(event) {
    return this.events.has(event) ? this.events.get(event).length : 0;
  }
}

// Export for module systems or global use
if (typeof module !== "undefined" && module.exports) {
  module.exports = EventEmitter;
} else {
  window.EventEmitter = EventEmitter;
}
