# WebKit Bugzilla 209753: pushState and back trigger page reloading when called in iframe

https://bugs.webkit.org/show_bug.cgi?id=209753

Status at the time of reading: NEW (Component: History, Version: Safari 13).

> When an `iframe` calls `window.history.pushState` and then `window.history.back`, the parent window's reloading.

> Fire event `popstate` without reload.

(the expected behaviour)

Steps to reproduce:

> Create iframe, add to DOM on parent page

> Remove iframe from DOM on parent page

> Create another iframe, load some app in it on parent page

> In an app iframe, call `window.history.pushState(...)`

> In an app iframe, call `window.history.back(...)`

> Got reload instead of expected popstate event
