/* CRO_TEST __MANIFEST__ */
(function () {
  'use strict';
  var config = __CONFIG__;
  if (location.origin !== config.target.origin || location.pathname !== config.target.pathname) return;
  var registry = window.__croTests = window.__croTests || Object.create(null);
  if (Object.prototype.hasOwnProperty.call(registry, config.id)) return;
  var state = registry[config.id] = { applied: false, errors: [], timedOut: false };
  var seen = config.changes.map(function () { return new WeakSet(); });
  var observer;
  var timer;
  function stop() {
    if (observer) observer.disconnect();
    clearTimeout(timer);
  }
  function apply() {
    try {
      var groups = config.changes.map(function (change) {
        return document.querySelectorAll(change.selector);
      });
      if (!groups.every(function (nodes, i) { return nodes.length === config.changes[i].count; })) return;
      if (config.css && !document.getElementById('cro-' + config.id + '-style')) {
        var style = document.createElement('style');
        style.id = 'cro-' + config.id + '-style';
        style.textContent = config.css;
        (document.head || document.documentElement).appendChild(style);
      }
      groups.forEach(function (nodes, i) {
        var change = config.changes[i];
        Array.prototype.forEach.call(nodes, function (element) {
          if (seen[i].has(element)) return;
          element.setAttribute('data-cro-' + config.id, '');
          if (change.action === 'set_text') element.textContent = change.value;
          if (change.action === 'set_attribute') element.setAttribute(change.attribute, change.value);
          if (change.action === 'replace_html') element.innerHTML = change.value;
          if (change.action === 'insert_after') {
            var marker = 'cro-' + config.id + '-insert-' + i;
            var next = element.nextElementSibling;
            if (!next || next.getAttribute('data-cro-insert') !== marker) {
              var wrapper = document.createElement('div');
              wrapper.setAttribute('data-cro-insert', marker);
              wrapper.setAttribute('data-cro-' + config.id, '');
              wrapper.innerHTML = change.value;
              element.insertAdjacentElement('afterend', wrapper);
            }
          }
          seen[i].add(element);
        });
      });
      state.applied = true;
    } catch (error) {
      state.errors.push(String(error));
      stop();
      throw error;
    }
  }
  observer = new MutationObserver(apply);
  observer.observe(document.documentElement, { childList: true, subtree: true });
  timer = setTimeout(function () {
    state.timedOut = !state.applied;
    if (!state.applied) {
      var message = 'CRO ' + config.id + ': selectors did not match before timeout';
      state.errors.push(message);
      console.error(message);
    }
    stop();
  }, config.timeout_ms);
  apply();
}());
