/* ==========================================================================
   BARGAIN VAPE — site behaviour
   Animation is progressive enhancement: markup renders fully without JS, and
   a CDN failure can never leave a blank page.
   ========================================================================== */

(function () {
  "use strict";

  var root = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------------------------------------------------------- Age gate */

  // `onEnter` runs once the visitor can actually see the page — either straight
  // away (already verified) or after they confirm. Animations are started from
  // there because ScrollTrigger cannot measure a scroll-locked document.
  function initAgeGate(onEnter) {
    var gate = document.getElementById("age-gate");
    if (!gate) {
      onEnter();
      return;
    }

    var STORAGE_KEY = "bv_age_ok";
    var verified = false;
    try {
      verified = sessionStorage.getItem(STORAGE_KEY) === "1";
    } catch (e) {
      verified = false; // private mode — gate shows each visit, which is fine
    }

    if (verified) {
      onEnter();
      return;
    }

    var lastFocus = document.activeElement;
    gate.classList.add("is-open");
    document.body.classList.add("is-locked");

    var confirmBtn = gate.querySelector("[data-age-confirm]");
    var denyBtn = gate.querySelector("[data-age-deny]");
    if (confirmBtn) confirmBtn.focus();

    function close() {
      try {
        sessionStorage.setItem(STORAGE_KEY, "1");
      } catch (e) {
        /* no-op */
      }
      gate.classList.remove("is-open");
      document.body.classList.remove("is-locked");
      document.removeEventListener("keydown", onKeydown, true);
      if (lastFocus && lastFocus.focus) lastFocus.focus();
      onEnter();
    }

    // Focus trap — the gate is the only interactive region while open.
    function onKeydown(e) {
      if (e.key !== "Tab") return;
      var focusables = gate.querySelectorAll(
        'button:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])'
      );
      var visible = Array.prototype.filter.call(focusables, function (el) {
        return el.offsetParent !== null;
      });
      if (!visible.length) return;
      var first = visible[0];
      var last = visible[visible.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }

    document.addEventListener("keydown", onKeydown, true);

    if (confirmBtn) confirmBtn.addEventListener("click", close);
    if (denyBtn) {
      denyBtn.addEventListener("click", function () {
        gate.classList.add("is-denied");
        var back = gate.querySelector("[data-age-back]");
        if (back) back.focus();
      });
    }

    var backBtn = gate.querySelector("[data-age-back]");
    if (backBtn) {
      backBtn.addEventListener("click", function () {
        gate.classList.remove("is-denied");
        if (confirmBtn) confirmBtn.focus();
      });
    }
  }

  /* -------------------------------------------------------------- Navigation */

  function initNav() {
    var nav = document.querySelector(".nav");
    var toggle = document.querySelector(".nav__toggle");
    var links = document.getElementById("nav-links");
    if (!nav) return;

    var scrolled = false;
    function onScroll() {
      var isScrolled = window.scrollY > 16;
      if (isScrolled !== scrolled) {
        scrolled = isScrolled;
        nav.classList.toggle("is-scrolled", isScrolled);
      }
    }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    if (!toggle || !links) return;

    function setOpen(open) {
      toggle.setAttribute("aria-expanded", String(open));
      links.classList.toggle("is-open", open);
    }

    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });

    links.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setOpen(false);
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth >= 900) setOpen(false);
    });
  }

  /* -------------------------------------------------------------- Animations */

  function showAll() {
    root.classList.remove("js");
  }

  /* Scroll reveals.

     These are driven by IntersectionObserver and CSS transitions rather than by
     the animation library, because these elements start at opacity 0 — so
     whatever reveals them decides whether the CONTENT IS VISIBLE AT ALL, not
     merely whether it animates. Tying that to a CDN script was a mistake: if
     GSAP is slow, blocked, or its ticker is throttled (mobile browsers do this
     aggressively, and any backgrounded tab does it), the page silently renders
     blank sections. IntersectionObserver has no such dependency, and CSS
     transitions run on the compositor even when the main thread is busy.

     There is still a belt-and-braces timer at the end: if anything at all goes
     wrong, everything becomes visible. */
  function initReveals() {
    var groups = document.querySelectorAll(".reveal, .reveal-stagger");
    if (!groups.length) return;

    function reveal(el) {
      el.classList.add("is-in");
    }

    if (!("IntersectionObserver" in window)) {
      showAll();
      return;
    }

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          reveal(entry.target);
          io.unobserve(entry.target);
        });
      },
      // Fire a little before the element is fully on screen so the motion is
      // finishing, not starting, by the time the reader reaches it.
      { rootMargin: "0px 0px -8% 0px", threshold: 0.01 }
    );

    Array.prototype.forEach.call(groups, function (el) {
      if (el.classList.contains("reveal-stagger")) {
        Array.prototype.forEach.call(el.children, function (kid, i) {
          // Cap the total so a long grid does not trail on for seconds.
          kid.style.transitionDelay = Math.min(i * 55, 385) + "ms";
        });
      }
      io.observe(el);
    });

    // Failsafe: nothing should ever stay invisible. If an element has not been
    // revealed a few seconds in, show it regardless of what the observer thinks.
    window.setTimeout(function () {
      Array.prototype.forEach.call(groups, function (el) {
        if (!el.classList.contains("is-in")) reveal(el);
      });
    }, 3000);
  }

  var animationsStarted = false;

  function initAnimations() {
    if (animationsStarted) return;
    animationsStarted = true;

    if (reduceMotion) {
      showAll();
      return;
    }

    // Runs first and without GSAP, so content appears even if the library never
    // arrives. Everything below this line is decorative flourish.
    initReveals();

    if (!window.gsap || !window.ScrollTrigger) return;

    var gsap = window.gsap;
    gsap.registerPlugin(window.ScrollTrigger);

    var EASE = "power3.out";

    // Hero — plays on load, no scroll trigger
    var heroLines = document.querySelectorAll("[data-hero-line]");
    if (heroLines.length) {
      gsap.set(heroLines, { yPercent: 105 });
      gsap.to(heroLines, {
        yPercent: 0,
        duration: 0.95,
        ease: "expo.out",
        stagger: 0.08,
        delay: 0.12,
      });
    }

    var heroFade = document.querySelectorAll("[data-hero-fade]");
    if (heroFade.length) {
      gsap.fromTo(
        heroFade,
        { opacity: 0, y: 20 },
        { opacity: 1, y: 0, duration: 0.8, ease: EASE, stagger: 0.1, delay: 0.45 }
      );
    }

    var heroVisual = document.querySelector("[data-hero-visual]");
    if (heroVisual) {
      gsap.fromTo(
        heroVisual,
        { opacity: 0, scale: 0.9, y: 34 },
        { opacity: 1, scale: 1, y: 0, duration: 1.3, ease: "expo.out", delay: 0.25 }
      );

      // Gentle float — reads as "product on display", not a bounce
      gsap.to(heroVisual, {
        y: -14,
        duration: 3.6,
        ease: "sine.inOut",
        repeat: -1,
        yoyo: true,
        delay: 1.5,
      });
    }

    // Ambient blobs — slow oscillation, transform only
    document.querySelectorAll(".atmos__blob").forEach(function (blob, i) {
      gsap.to(blob, {
        x: i % 2 === 0 ? 90 : -70,
        y: i % 2 === 0 ? -50 : 60,
        duration: 16 + i * 5,
        ease: "sine.inOut",
        repeat: -1,
        yoyo: true,
      });
    });

    // Scroll reveals are deliberately NOT handled here — see initReveals().

    // Case artwork drifts slightly slower than the page — depth without jank.
    // Desktop only: a scrubbed parallax fights the address-bar resize on phones
    // and costs more than the effect is worth on a small screen.
    if (window.matchMedia("(min-width: 900px)").matches) {
      gsap.utils.toArray("[data-parallax]").forEach(function (el) {
        gsap.to(el, {
          yPercent: -8,
          ease: "none",
          scrollTrigger: {
            trigger: el,
            start: "top bottom",
            end: "bottom top",
            scrub: 0.6,
          },
        });
      });
    }

    // Count-up stats
    gsap.utils.toArray("[data-count]").forEach(function (el) {
      var target = parseFloat(el.getAttribute("data-count"));
      var prefix = el.getAttribute("data-prefix") || "";
      var suffix = el.getAttribute("data-suffix") || "";
      var decimals = parseInt(el.getAttribute("data-decimals") || "0", 10);
      var obj = { v: 0 };
      gsap.to(obj, {
        v: target,
        duration: 1.5,
        ease: "power2.out",
        scrollTrigger: { trigger: el, start: "top 90%", once: true },
        onUpdate: function () {
          el.textContent = prefix + obj.v.toFixed(decimals) + suffix;
        },
      });
    });

    window.addEventListener("load", function () {
      window.ScrollTrigger.refresh();
    });
  }

  /* ------------------------------------------------------------ Hero video */

  function initHeroVideo() {
    var video = document.querySelector(".hero__video");
    if (!video) return;

    var src = video.getAttribute("data-src");
    if (!src) return;

    // Never autoplay for someone who asked for less motion — the poster frame
    // is a finished image on its own.
    if (reduceMotion) return;

    // Respect data saver and genuinely slow connections; the hero is decorative.
    var conn =
      navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    if (conn) {
      if (conn.saveData) return;
      if (/(^|-)(2g|slow-2g)$/.test(conn.effectiveType || "")) return;
    }

    video.muted = true; // belt and braces: autoplay is only allowed when muted
    video.setAttribute("muted", "");
    video.playsInline = true;

    video.addEventListener(
      "playing",
      function () {
        video.classList.add("is-playing");
      },
      { once: true }
    );

    // If it cannot play for any reason, the poster simply stays put.
    video.addEventListener("error", function () {
      video.classList.remove("is-playing");
    });

    video.preload = "auto";
    video.src = src;

    var attempt = video.play();
    if (attempt && typeof attempt.catch === "function") {
      attempt.catch(function () {
        video.classList.remove("is-playing");
      });
    }
  }

  /* --------------------------------------------- Flavor front/back switch */

  /* Each flavour tile cycles through three views of the same product:
     the sleeve a customer picks up, its back panel, and the 10-count box a
     retailer actually stocks. */
  /* `label` names what is ON SCREEN NOW, not what comes next. Labelling the
     next view made the caption read as though it were mislabelling the photo. */
  var FACES = [
    { key: "front", label: "Sleeve Front", now: "the front of the sleeve" },
    { key: "back", label: "Sleeve Back", now: "the back of the sleeve" },
    { key: "box", label: "10-ct Box", now: "the 10-count box" }
  ];

  function initFaceToggles() {
    document.querySelectorAll(".flavor-card__stack").forEach(function (stack) {
      var card = stack.closest(".flavor-card");
      if (!card) return;
      var name = stack.getAttribute("data-name") || "this product";
      var label = stack.querySelector("[data-flip-label]");
      var index = 0;

      function apply() {
        var face = FACES[index];
        FACES.forEach(function (f) {
          card.classList.toggle("show-" + f.key, f.key === face.key);
        });
        if (label) label.textContent = face.label;
        stack.setAttribute(
          "aria-label",
          "Packaging for " + name + ", showing " + face.now +
            ". Activate to show the next view."
        );
      }

      stack.addEventListener("click", function () {
        index = (index + 1) % FACES.length;
        apply();
      });

      apply();
    });
  }

  /* ------------------------------------------------------- Wholesale form */

  function initForm() {
    var form = document.getElementById("wholesale-form");
    if (!form) return;

    var status = document.getElementById("form-status");
    var submitBtn = form.querySelector("[type='submit']");
    var submitLabel = submitBtn ? submitBtn.textContent : "";

    /* Point every control at its own error text with aria-describedby.
       role="alert" alone only announces the error at the moment it appears — a
       screen reader user who tabs back to the field later would hear the label
       and nothing about why it was rejected. Wiring it here rather than in the
       markup keeps the twelve fields from drifting out of sync. */
    form
      .querySelectorAll("input:not([type=hidden]), select, textarea")
      .forEach(function (input) {
        var field = input.closest(".field");
        if (!field || !input.id) return;
        var errEl = field.querySelector(".field__error");
        if (!errEl) return;

        if (!errEl.id) errEl.id = input.id + "-error";

        var described = (input.getAttribute("aria-describedby") || "").split(/\s+/);
        if (described.indexOf(errEl.id) === -1) {
          described.push(errEl.id);
          input.setAttribute("aria-describedby", described.join(" ").trim());
        }
      });

    function setFieldError(input, message) {
      var field = input.closest(".field");
      if (!field) return;
      var errEl = field.querySelector(".field__error");
      if (message) {
        field.classList.add("has-error");
        input.setAttribute("aria-invalid", "true");
        if (errEl) errEl.textContent = message;
      } else {
        field.classList.remove("has-error");
        input.removeAttribute("aria-invalid");
      }
    }

    function validateField(input) {
      if (!input.checkValidity()) {
        var msg = input.validity.valueMissing
          ? "This field is required."
          : input.validity.typeMismatch
          ? "Enter a valid " + (input.type === "email" ? "email address" : "value") + "."
          : "Please check this field.";
        setFieldError(input, msg);
        return false;
      }
      setFieldError(input, "");
      return true;
    }

    // Validate on blur, never mid-typing
    form.querySelectorAll("input, select, textarea").forEach(function (input) {
      input.addEventListener("blur", function () {
        if (input.value !== "" || input.required) validateField(input);
      });
      input.addEventListener("input", function () {
        if (input.closest(".field").classList.contains("has-error")) validateField(input);
      });
    });

    function showStatus(type, message) {
      if (!status) return;
      status.className = "form-status is-visible form-status--" + type;
      var textEl = status.querySelector("[data-status-text]");
      if (textEl) textEl.textContent = message;
      var okIcon = status.querySelector("[data-icon-ok]");
      var errIcon = status.querySelector("[data-icon-err]");
      if (okIcon) okIcon.style.display = type === "ok" ? "block" : "none";
      if (errIcon) errIcon.style.display = type === "err" ? "block" : "none";
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();

      var firstInvalid = null;
      form.querySelectorAll("input, select, textarea").forEach(function (input) {
        if (!validateField(input) && !firstInvalid) firstInvalid = input;
      });

      if (firstInvalid) {
        firstInvalid.focus();
        showStatus("err", "Please fix the highlighted fields and try again.");
        return;
      }

      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Sending…";
      }

      // Netlify accepts a form post at any path on the site and routes it by the
      // form-name field, so post to the root rather than the action (the action
      // is the no-JavaScript redirect target, not an API endpoint). The body must
      // be url-encoded — Netlify does not parse multipart for this.
      var body = new URLSearchParams(new FormData(form)).toString();

      fetch("/", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body,
      })
        .then(function (res) {
          if (!res.ok) throw new Error("Request failed");
          form.reset();
          showStatus(
            "ok",
            "Thanks — your inquiry is in. We typically respond to wholesale requests within one business day."
          );
        })
        .catch(function () {
          // Covers local previews (where Netlify is not running) and genuine
          // outages. Hand the visitor their own mail client rather than losing
          // what they typed.
          var lines = [];
          new FormData(form).forEach(function (value, key) {
            if (key !== "form-name" && key !== "bot-field" && String(value).trim() !== "") {
              lines.push(key + ": " + value);
            }
          });
          var mailto =
            "mailto:" +
            (form.getAttribute("data-fallback-email") || "") +
            "?subject=" +
            encodeURIComponent("Wholesale inquiry — Bargain Vape") +
            "&body=" +
            encodeURIComponent(lines.join("\n"));
          showStatus(
            "err",
            "We could not send that from here. Opening your email app with the inquiry " +
              "pre-filled instead — or write to us directly at the address above."
          );
          window.location.href = mailto;
        })
        .finally(function () {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = submitLabel;
          }
        });
    });
  }

  /* -------------------------------------------------------------- Boot */

  function boot() {
    initNav();
    initForm();
    initFaceToggles();
    initAgeGate(function () {
      initHeroVideo();
      initAnimations();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  // Last-resort guard: if anything above threw before animations ran, make sure
  // no content is left hidden.
  setTimeout(function () {
    if (root.classList.contains("js") && !window.gsap) showAll();
  }, 2500);
})();
