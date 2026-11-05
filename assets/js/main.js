/* Reverb Content – közös szkriptek.
   GSAP + ScrollTrigger + Lenis (helyi másolat, assets/js/vendor) a mozgáshoz; ha nem töltődnek be,
   vagy csökkentett mozgás van beállítva (.is-still), minden tartalom statikusan, teljes állapotban látszik. */
(function () {
  "use strict";

  var root = document.documentElement;
  var reduce = root.classList.contains("is-still") || window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce) root.classList.add("is-still");
  var fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var hasGsap = typeof window.gsap !== "undefined" && typeof window.ScrollTrigger !== "undefined";
  var motion = hasGsap && !reduce;

  var pad = function (n) { return n < 10 ? "0" + n : String(n); };
  var timecode = function (seconds) {
    var f = Math.floor(seconds * 25);
    var s = Math.floor(f / 25);
    return pad(Math.floor(s / 3600)) + ":" + pad(Math.floor(s / 60) % 60) + ":" + pad(s % 60) + ":" + pad(f % 25);
  };

  if (motion) {
    gsap.registerPlugin(ScrollTrigger);
    root.classList.add("js-gsap");
  }

  /* ---------- Fejléc, mobilmenü ---------- */
  var header = document.querySelector(".site-header");
  var toggle = document.querySelector(".nav-toggle");
  var mobileNav = document.getElementById("mobile-nav");
  var lenis = null;
  var lastY = window.scrollY;

  function onScroll() {
    var y = window.scrollY;
    if (header) {
      header.classList.toggle("is-scrolled", y > 24);
      header.classList.toggle("is-hidden", y > 400 && y > lastY + 2);
      if (y < lastY - 2) header.classList.remove("is-hidden");
    }
    lastY = y;
  }
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
  // billentyűzettel a fejlécbe lépve mindig látszódjon
  if (header) header.addEventListener("focusin", function () { header.classList.remove("is-hidden"); });

  /* Mobilmenü: nyitáskor a háttér inert, a fókusz az első linkre kerül, a Tab a menün belül
     körbejár, Escape vagy bezárás után a fókusz visszatér a nyitógombra. */
  var menuOpen = false;
  var backdrop = function () {
    return Array.prototype.slice.call(document.querySelectorAll(".skip, .brand, main, .site-footer, .cookie, .motion-toggle"));
  };
  var menuFocusables = function () {
    return [toggle].concat(Array.prototype.slice.call(mobileNav.querySelectorAll("a[href], button:not([disabled])")));
  };
  function setMenu(open, returnFocus) {
    if (!toggle || !mobileNav) return;
    menuOpen = open;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.querySelector(".nav-toggle__text").textContent = open ? "Bezárás" : "Menü";
    header.classList.toggle("is-open", open);
    mobileNav.classList.toggle("is-open", open);
    mobileNav.inert = !open;
    backdrop().forEach(function (el) { el.inert = open; });
    document.body.style.overflow = open ? "hidden" : "";
    if (lenis) { if (open) lenis.stop(); else lenis.start(); }
    if (open) {
      var first = mobileNav.querySelector("a[href]");
      if (first) first.focus();
    } else if (returnFocus) {
      toggle.focus();
    }
  }
  if (toggle && mobileNav) {
    mobileNav.inert = true;
    toggle.addEventListener("click", function () { setMenu(!menuOpen, true); });
    mobileNav.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false, false); });
    document.addEventListener("keydown", function (e) {
      if (!menuOpen) return;
      if (e.key === "Escape") { e.preventDefault(); setMenu(false, true); return; }
      if (e.key !== "Tab") return;
      var items = menuFocusables();
      var i = items.indexOf(document.activeElement);
      if (e.shiftKey && (i <= 0)) { e.preventDefault(); items[items.length - 1].focus(); }
      else if (!e.shiftKey && (i === items.length - 1 || i === -1)) { e.preventDefault(); items[0].focus(); }
    });
    window.matchMedia("(min-width: 961px)").addEventListener("change", function (mq) { if (mq.matches && menuOpen) setMenu(false, false); });
  }

  /* ---------- Mozgás szüneteltetése (látható kapcsoló, tárolt preferencia) ----------
     A végtelen mozgást (futó sávok, időkód, REC-jel, fényfolt) állítja meg; a görgetéshez
     kötött effektek a görgetéssel együtt állnak meg. */
  var MKEY = "rvb-motion";
  var pausers = [];
  var motionToggles = Array.prototype.slice.call(document.querySelectorAll("[data-motion-toggle]"));
  var isPaused = root.classList.contains("is-paused");
  var applyPause = function (p) {
    isPaused = p;
    root.classList.toggle("is-paused", p);
    pausers.forEach(function (fn) { fn(p); });
    motionToggles.forEach(function (b) {
      b.setAttribute("aria-pressed", String(p));
      b.querySelector("[data-motion-label]").textContent = p ? "Mozgás indítása" : "Mozgás szüneteltetése";
    });
  };
  motionToggles.forEach(function (b) {
    b.addEventListener("click", function () {
      applyPause(!isPaused);
      try { localStorage.setItem(MKEY, isPaused ? "paused" : "on"); } catch (e) { /* privát mód */ }
    });
  });
  applyPause(isPaused);

  /* ---------- Munkák: némított előnézet ----------
     Csak látótérben, és csak ha a mozgás engedélyezett; különben a poszterkép látszik.
     preload="none": a videó csak az első lejátszáskor töltődik. */
  var previews = Array.prototype.slice.call(document.querySelectorAll("video[data-preview]"));
  if (previews.length && !reduce && "IntersectionObserver" in window) {
    var inView = [];
    var syncPreview = function (v) {
      if (!isPaused && inView.indexOf(v) > -1) {
        var pr = v.play();
        if (pr && pr.catch) pr.catch(function () { /* automatikus lejátszás tiltva: marad a poszter */ });
      } else if (!v.paused) v.pause();
    };
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var i = inView.indexOf(en.target);
        if (en.isIntersecting && i < 0) inView.push(en.target);
        if (!en.isIntersecting && i > -1) inView.splice(i, 1);
        syncPreview(en.target);
      });
    }, { threshold: 0.35 });
    previews.forEach(function (v) { io.observe(v); });
    pausers.push(function () { previews.forEach(syncPreview); });
  }

  /* Esettanulmány: egyszerre csak egy hangos videó szóljon */
  document.addEventListener("play", function (e) {
    if (!e.target.controls) return;
    document.querySelectorAll("video[controls]").forEach(function (v) { if (v !== e.target && !v.paused) v.pause(); });
  }, true);

  /* ---------- Gördülő feliratok ---------- */
  document.querySelectorAll("[data-roll]").forEach(function (el) {
    var t = el.textContent.trim();
    var wrap = document.createElement("span");
    wrap.className = "roll";
    var inner = document.createElement("span");
    inner.className = "roll__in";
    inner.setAttribute("data-t", t);
    inner.textContent = t;
    wrap.appendChild(inner);
    el.textContent = "";
    el.appendChild(wrap);
  });

  /* ---------- Időkód a keresőnézetben ---------- */
  var tc = document.querySelector("[data-timecode]");
  if (tc && !reduce) {
    var elapsed = 0;
    var last = performance.now();
    (function tick(now) {
      if (!isPaused) {
        elapsed += now - last;
        tc.textContent = timecode(elapsed / 1000);
      }
      last = now;
      requestAnimationFrame(tick);
    })(last);
  }

  /* ---------- Szavakra bontás (beúszáshoz) ---------- */
  function splitWords(el, cls) {
    var out = [];
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.textContent.split(/([ \t\n\r]+)/).forEach(function (p) {  // nem törő szóközön (pl. „70 000”) nem bontunk
            if (!p) return;
            if (/^[ \t\n\r]+$/.test(p)) { frag.appendChild(document.createTextNode(" ")); return; }
            var w = document.createElement("span");
            w.className = cls;
            var i = document.createElement("span");
            i.className = cls + "__in";
            i.textContent = p;
            w.appendChild(i);
            frag.appendChild(w);
            out.push(i);
          });
          node.replaceChild(frag, n);
        } else if (n.nodeType === 1 && n.tagName !== "BR") {
          if (n.classList.contains("ph")) {
            var w2 = document.createElement("span");
            w2.className = cls;
            var i2 = document.createElement("span");
            i2.className = cls + "__in";
            n.parentNode.insertBefore(w2, n);
            w2.appendChild(i2);
            i2.appendChild(n);
            out.push(i2);
          } else {
            walk(n);
          }
        }
      });
    })(el);
    return out;
  }

  if (motion) {
    /* ---------- Sima görgetés (asztali egér/trackpad) ---------- */
    if (fine && typeof window.Lenis !== "undefined") {
      lenis = new Lenis({ lerp: 0.11 });
      lenis.on("scroll", ScrollTrigger.update);
      gsap.ticker.add(function (t) { lenis.raf(t * 1000); });
      gsap.ticker.lagSmoothing(0);
    }

    document.addEventListener("click", function (e) {
      var a = e.target.closest('a[href*="#"]');
      if (!a) return;
      var url = new URL(a.href, window.location.href);
      if (url.pathname !== window.location.pathname || !url.hash) return;
      var target = document.getElementById(decodeURIComponent(url.hash.slice(1)));
      if (!target) return;
      e.preventDefault();
      if (lenis) lenis.scrollTo(target, { offset: -80, duration: 1.4 });
      else target.scrollIntoView({ behavior: "smooth" });
      history.pushState(null, "", url.hash);
      target.setAttribute("tabindex", "-1");
      target.focus({ preventScroll: true });
    });

    /* ---------- Bevezető (munkamenetenként egyszer) ---------- */
    var heroDelay = 0.1;
    var pre = document.querySelector(".preloader");
    if (root.classList.contains("is-intro") && pre) {
      heroDelay = 1.35;
      var tcPre = pre.querySelector(".preloader__tc");
      var frame = pre.querySelector(".preloader__frame");
      var vf = document.querySelector("[data-viewfinder]");
      var counter = { s: 0 };
      if (lenis) lenis.stop();
      var tl = gsap.timeline({
        onComplete: function () {
          root.classList.remove("is-intro");
          if (lenis) lenis.start();
        }
      });
      tl.to(counter, { s: 1, duration: 0.9, ease: "none", onUpdate: function () { tcPre.textContent = timecode(counter.s); } });
      if (vf) {
        var r = vf.getBoundingClientRect();
        tl.to(frame, { top: r.top, left: r.left, right: window.innerWidth - r.right, bottom: window.innerHeight - r.bottom, duration: 0.75, ease: "expo.inOut" }, 0.55);
      }
      tl.to(pre, { autoAlpha: 0, duration: 0.4, ease: "power2.out" }, 1.2);
    }

    /* ---------- Címsorok beúszása ---------- */
    document.querySelectorAll("[data-split]").forEach(function (el) {
      var words = splitWords(el, "w");
      gsap.set(words, { yPercent: 115 });
      var anim = { yPercent: 0, duration: 1.15, ease: "expo.out", stagger: 0.045 };
      if (el.closest(".hero")) anim.delay = heroDelay;
      else anim.scrollTrigger = { trigger: el, start: "top 88%", once: true };
      gsap.to(words, anim);
    });

    gsap.utils.toArray("[data-reveal]").forEach(function (el) {
      var cfg = { y: 40, opacity: 0, duration: 1.1, ease: "expo.out" };
      // az aloldalak nyitóképén azonnal, máshol görgetésre jelenik meg
      if (el.closest(".page-hero")) cfg.delay = 0.35;
      else cfg.scrollTrigger = { trigger: el, start: "top 90%", once: true };
      gsap.from(el, cfg);
    });

    /* ---------- Hero ---------- */
    var hero = document.querySelector("[data-hero]");
    if (hero) {
      gsap.from(hero.querySelectorAll(".hero__aside > *, .hero__title .label"), { y: 28, opacity: 0, duration: 1.1, ease: "expo.out", stagger: 0.08, delay: heroDelay + 0.25 });
      gsap.to(hero.querySelector(".hero__body"), { yPercent: -14, opacity: 0.25, ease: "none", scrollTrigger: { trigger: hero, start: "top top", end: "bottom top", scrub: true } });
      gsap.to(hero.querySelector("[data-viewfinder]"), { "--l": "84px", ease: "none", scrollTrigger: { trigger: hero, start: "top top", end: "bottom top", scrub: true } });
      if (fine) {
        hero.addEventListener("pointermove", function (e) {
          var b = hero.getBoundingClientRect();
          hero.style.setProperty("--mx", ((e.clientX - b.left) / b.width) * 100 + "%");
          hero.style.setProperty("--my", ((e.clientY - b.top) / b.height) * 100 + "%");
        });
      }
    }
    root.classList.remove("js-pending");

    /* ---------- AFTERIMAGE: utókép a görgetés sebességéből ----------
       Csak mozgás közben jelenik meg; nyugalomban --e = 0, minden teljesen éles. */
    var echoTargets = Array.prototype.slice.call(document.querySelectorAll("[data-echo]"));
    if (echoTargets.length) {
      var echoTarget = 0;
      var echoCur = 0;
      var echoDir = 1;
      ScrollTrigger.create({
        start: 0,
        end: "max",
        onUpdate: function (self) {
          var v = self.getVelocity();
          echoDir = v >= 0 ? 1 : -1;
          echoTarget = Math.min(Math.abs(v) / 2600, 1);
        }
      });
      // belépéskor egy rövid utókép a hero címen, ami magától elhal
      var heroTitle = document.querySelector(".hero [data-echo]");
      if (heroTitle) {
        var intro = { e: 0.9 };
        heroTitle.style.setProperty("--e", "0.9");
        gsap.to(intro, { e: 0, duration: 1.6, delay: heroDelay + 0.2, ease: "power3.out", onUpdate: function () { heroTitle.style.setProperty("--e", intro.e.toFixed(3)); } });
      }
      gsap.ticker.add(function () {
        echoTarget *= 0.88;
        echoCur += (echoTarget - echoCur) * 0.18;
        if (echoCur < 0.003 && echoTarget < 0.003) {
          if (echoCur !== 0) {
            echoCur = 0;
            echoTargets.forEach(function (el) { el.style.setProperty("--e", "0"); el.style.setProperty("--ed", "1"); });
          }
          return;
        }
        var val = echoCur.toFixed(3);
        echoTargets.forEach(function (el) { el.style.setProperty("--e", val); el.style.setProperty("--ed", String(echoDir)); });
      });
    }

    /* ---------- Futó sávok (görgetésre gyorsulnak, hoverre lassulnak) ---------- */
    document.querySelectorAll("[data-marquee]").forEach(function (m) {
      var track = m.querySelector("[data-marquee-track]");
      var base = 1;
      var boost = 0;
      var tw = gsap.to(track, { xPercent: -50, ease: "none", duration: parseFloat(m.getAttribute("data-marquee")) || 40, repeat: -1 });
      ScrollTrigger.create({ trigger: m, start: "top bottom", end: "bottom top", onUpdate: function (self) { boost = Math.max(boost, Math.min(Math.abs(self.getVelocity()) / 400, 4)); } });
      gsap.ticker.add(function () { boost *= 0.94; tw.timeScale(base + boost); });
      m.addEventListener("pointerenter", function () { base = 0.25; });
      m.addEventListener("pointerleave", function () { base = 1; });
      pausers.push(function (p) { if (p) tw.pause(); else tw.play(); });
      if (isPaused) tw.pause();
    });

    /* ---------- Három beszállító → egy csapat ---------- */
    var merge = document.querySelector("[data-merge]");
    if (merge) {
      var stage = merge.querySelector(".merge__stage");
      var nodes = merge.querySelectorAll(".merge__node");
      var gaps = merge.querySelectorAll(".merge__gap");
      var gapStart = function () {
        var free = stage.clientWidth - nodes.length * nodes[0].offsetWidth - 48;
        return Math.max(12, Math.min(free / 2, window.innerWidth * 0.16));
      };
      var mt = gsap.timeline({ scrollTrigger: { trigger: merge, start: "top top", end: "+=75%", pin: true, scrub: 0.6, invalidateOnRefresh: true } });
      mt.fromTo(gaps, { width: gapStart, opacity: 1 }, { width: 6, ease: "power2.inOut", duration: 1 }, 0)
        .to(gaps, { opacity: 0, duration: 0.25 }, 0.75)
        .to(merge.querySelectorAll(".merge__node .label"), { opacity: 0, y: -8, duration: 0.3 }, 0.5)
        .to(merge.querySelector(".merge__a"), { opacity: 0, yPercent: -25, duration: 0.35 }, 0.4)
        .fromTo(merge.querySelector(".merge__b"), { opacity: 0, yPercent: 25 }, { opacity: 1, yPercent: 0, duration: 0.35 }, 0.6)
        .fromTo(merge.querySelector(".merge__frame"), { opacity: 0, "--l": "0px" }, { opacity: 1, "--l": "28px", duration: 0.4, ease: "power2.out" }, 0.72);
    }

    /* ---------- Egy film → formátumcsomag ---------- */
    var reverb = document.querySelector("[data-reverb]");
    if (reverb) {
      var stageEl = reverb.querySelector(".reverb__stage");
      var fan = reverb.querySelector(".fan");
      var master = reverb.querySelector(".fan__frame--master");
      var frames = gsap.utils.toArray(reverb.querySelectorAll(".fan__frame:not(.fan__frame--master)"));
      // az utókép az adott formátumtól a főfilm felé mutat
      var setDirections = function () {
        frames.forEach(function (f) {
          var dx = fan.clientWidth / 2 - (f.offsetLeft + f.offsetWidth / 2);
          var dy = fan.clientHeight / 2 - (f.offsetTop + f.offsetHeight / 2);
          var len = Math.hypot(dx, dy) || 1;
          f.style.setProperty("--dx", (dx / len).toFixed(3));
          f.style.setProperty("--dy", (dy / len).toFixed(3));
        });
      };
      setDirections();
      ScrollTrigger.addEventListener("refreshInit", setDirections);
      var ft = gsap.timeline({ scrollTrigger: { trigger: stageEl, start: "top top", end: "+=110%", pin: true, scrub: 0.6, invalidateOnRefresh: true } });
      ft.from(master, { scale: 1.3, duration: 1, ease: "power2.out" }, 0);
      frames.forEach(function (f, i) {
        ft.from(f, {
          x: function () { return fan.clientWidth / 2 - (f.offsetLeft + f.offsetWidth / 2); },
          y: function () { return fan.clientHeight / 2 - (f.offsetTop + f.offsetHeight / 2); },
          scale: 0.45,
          opacity: 0,
          ease: "power3.out",
          duration: 1
        }, 0.15 + i * 0.16);
      });
      reverb.querySelectorAll(".tally__item").forEach(function (it, i) {
        ft.to(it, { color: "#25f79c", duration: 0.2 }, 0.3 + i * 0.28);
      });
    }

    /* ---------- Kijelentés: szavanként kivilágosodik ---------- */
    document.querySelectorAll("[data-reveal-words]").forEach(function (el) {
      var words = splitWords(el, "rw");
      gsap.fromTo(words, { opacity: 0.14 }, { opacity: 1, ease: "none", stagger: 0.1, scrollTrigger: { trigger: el, start: "top 80%", end: "bottom 50%", scrub: true } });
    });

    gsap.utils.toArray("[data-stagger]").forEach(function (group) {
      gsap.from(group.children, { y: 70, opacity: 0, duration: 1.1, ease: "expo.out", stagger: 0.08, scrollTrigger: { trigger: group, start: "top 86%", once: true } });
    });

    /* ---------- Vízszintes idővonal (csak ebben az egy szekcióban, asztali nézetben) ---------- */
    var hs = document.querySelector("[data-hscroll]");
    if (hs) {
      gsap.matchMedia().add("(min-width: 768px)", function () {
        hs.classList.add("is-pinned");
        var track = hs.querySelector(".hscroll__track");
        var vp = hs.querySelector(".hscroll__viewport");
        var ticks = hs.querySelector(".hscroll__ticks");
        var tcEl = hs.querySelector(".hscroll__tc");
        var dist = function () { return Math.max(0, track.scrollWidth - vp.clientWidth); };
        var tw = gsap.to(track, {
          x: function () { return -dist(); },
          ease: "none",
          scrollTrigger: {
            trigger: hs,
            start: "top top",
            end: function () { return "+=" + dist(); },
            pin: true,
            scrub: 0.6,
            invalidateOnRefresh: true,
            onUpdate: function (self) {
              gsap.set(ticks, { x: -dist() * self.progress });
              tcEl.textContent = timecode(self.progress * 84);
            }
          }
        });
        hs.querySelectorAll(".clip").forEach(function (c) {
          gsap.from(c.querySelector(".ico"), { y: 50, opacity: 0, duration: 0.9, ease: "expo.out", scrollTrigger: { trigger: c, containerAnimation: tw, start: "left 96%", toggleActions: "play none none reverse" } });
        });
        // billentyűzettel bejárva a fókuszált kártya kerüljön képbe
        hs.addEventListener("focusin", function (e) {
          var card = e.target.closest(".clip, .hscroll__outro");
          if (!card || !tw.scrollTrigger) return;
          var st = tw.scrollTrigger;
          var p = Math.min(1, Math.max(0, (card.offsetLeft - vp.clientWidth * 0.3) / dist()));
          var y = st.start + (st.end - st.start) * p;
          if (lenis) lenis.scrollTo(y, { immediate: true }); else window.scrollTo(0, y);
        });
        return function () {
          hs.classList.remove("is-pinned");
          gsap.set([track, ticks], { clearProps: "transform" });
        };
      });
      // mobilon natív lapozás: a vonalzó és az időkód követi
      gsap.matchMedia().add("(max-width: 767px)", function () {
        var vp = hs.querySelector(".hscroll__viewport");
        var ticks = hs.querySelector(".hscroll__ticks");
        var tcEl = hs.querySelector(".hscroll__tc");
        var sync = function () {
          var max = vp.scrollWidth - vp.clientWidth || 1;
          ticks.style.transform = "translateX(" + -vp.scrollLeft + "px)";
          tcEl.textContent = timecode((vp.scrollLeft / max) * 84);
        };
        vp.addEventListener("scroll", sync, { passive: true });
        return function () { vp.removeEventListener("scroll", sync); ticks.style.transform = ""; };
      });
    }

    /* ---------- Munkák: letterbox-nyitás ---------- */
    gsap.utils.toArray(".work__frame").forEach(function (fr) {
      gsap.fromTo(fr, { clipPath: "inset(14% 0% 14% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", ease: "none", scrollTrigger: { trigger: fr, start: "top 95%", end: "top 45%", scrub: true } });
      var v = fr.querySelector(".work__video");
      if (v) gsap.fromTo(v, { scale: 1.18 }, { scale: 1, ease: "none", scrollTrigger: { trigger: fr, start: "top bottom", end: "bottom top", scrub: true } });
    });

    /* ---------- Folyamat: a vonal végigrajzolódik ---------- */
    var flow = document.querySelector("[data-flow]");
    if (flow) {
      var steps = flow.querySelectorAll(".flow__step");
      gsap.fromTo(flow, { "--p": 0 }, {
        "--p": 1,
        ease: "none",
        scrollTrigger: {
          trigger: flow,
          start: "top 75%",
          end: "bottom 60%",
          scrub: true,
          onUpdate: function (self) {
            steps.forEach(function (s, i) { s.classList.toggle("is-on", self.progress >= i / Math.max(1, steps.length - 1) - 0.02); });
          }
        }
      });
    }

    /* ---------- Görgetési sáv ---------- */
    var scr = document.querySelector(".scrubber");
    if (scr) {
      var fill = scr.querySelector(".scrubber__fill");
      var stc = scr.querySelector(".scrubber__tc");
      ScrollTrigger.create({ start: 0, end: "max", onUpdate: function (self) {
        fill.style.transform = "scaleX(" + self.progress.toFixed(4) + ")";
        stc.textContent = timecode(self.progress * 90);
      } });
    }

    /* ---------- Hover: döntés, mágnes, kurzor (csak egérrel) ---------- */
    if (fine) {
      document.querySelectorAll("[data-tilt]").forEach(function (el) {
        var rx = gsap.quickTo(el, "rotationX", { duration: 0.7, ease: "power3.out" });
        var ry = gsap.quickTo(el, "rotationY", { duration: 0.7, ease: "power3.out" });
        gsap.set(el, { transformPerspective: 900 });
        el.addEventListener("pointermove", function (e) {
          var b = el.getBoundingClientRect();
          var px = (e.clientX - b.left) / b.width - 0.5;
          var py = (e.clientY - b.top) / b.height - 0.5;
          ry(px * 9);
          rx(-py * 9);
          el.style.setProperty("--gx", (px + 0.5) * 100 + "%");
          el.style.setProperty("--gy", (py + 0.5) * 100 + "%");
        });
        el.addEventListener("pointerleave", function () { rx(0); ry(0); });
      });

      document.querySelectorAll("[data-magnetic]").forEach(function (el) {
        var xTo = gsap.quickTo(el, "x", { duration: 0.6, ease: "power3.out" });
        var yTo = gsap.quickTo(el, "y", { duration: 0.6, ease: "power3.out" });
        var box = null;
        el.addEventListener("pointerenter", function () { box = el.getBoundingClientRect(); });
        el.addEventListener("pointermove", function (e) {
          if (!box) return;
          xTo((e.clientX - (box.left + box.width / 2)) * 0.28);
          yTo((e.clientY - (box.top + box.height / 2)) * 0.4);
        });
        el.addEventListener("pointerleave", function () { xTo(0); yTo(0); box = null; });
      });

      var cur = document.querySelector(".cursor");
      if (cur) {
        root.classList.add("has-cursor");
        var dot = cur.querySelector(".cursor__dot");
        var ring = cur.querySelector(".cursor__ring");
        var lab = cur.querySelector(".cursor__label");
        var dX = gsap.quickTo(dot, "x", { duration: 0.08 });
        var dY = gsap.quickTo(dot, "y", { duration: 0.08 });
        var rX = gsap.quickTo(ring, "x", { duration: 0.45, ease: "power3.out" });
        var rY = gsap.quickTo(ring, "y", { duration: 0.45, ease: "power3.out" });
        window.addEventListener("pointermove", function (e) {
          dX(e.clientX); dY(e.clientY); rX(e.clientX); rY(e.clientY);
          cur.classList.add("is-visible");
        }, { passive: true });
        document.addEventListener("pointerover", function (e) {
          var t = e.target.closest("a, button, summary, label, input, select, textarea, [data-cursor]");
          var labeled = e.target.closest("[data-cursor]");
          cur.classList.toggle("is-label", !!labeled);
          lab.textContent = labeled ? labeled.getAttribute("data-cursor") : "";
          cur.classList.toggle("is-link", !!t && !labeled);
          cur.classList.toggle("is-text", !!t && /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName));
        });
        document.documentElement.addEventListener("pointerleave", function () { cur.classList.remove("is-visible"); });
      }
    }

    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { ScrollTrigger.refresh(); });
    window.addEventListener("load", function () { ScrollTrigger.refresh(); });
  } else {
    root.classList.remove("is-intro", "js-pending");
  }

  /* ---------- Ajánlatkérő űrlap ---------- */
  var form = document.querySelector("[data-lead-form]");
  if (form) {
    var status = form.querySelector(".form__status");
    var tema = new URLSearchParams(window.location.search).get("tema");
    if (tema) {
      var pre2 = form.querySelector('input[name="tema"][data-slug="' + tema.replace(/[^a-z-]/g, "") + '"]');
      if (pre2) pre2.checked = true;
    }
    var messages = {
      nev: "Add meg a neved.",
      ceg: "Add meg a céged nevét.",
      email: "Adj meg egy érvényes e-mail-címet, például nev@ceg.hu.",
      adatkezeles: "Az elküldéshez fogadd el az adatkezelési tájékoztatót."
    };
    var validate = function (input) {
      var field = input.closest(".field") || input.closest(".consent");
      var ok = input.type === "checkbox" ? input.checked : input.checkValidity() && input.value.trim() !== "";
      if (!input.required) ok = input.checkValidity();
      if (field) {
        field.classList.toggle("is-invalid", !ok);
        var err = field.querySelector(".field__error");
        if (err) err.textContent = ok ? "" : (messages[input.name] || "Töltsd ki ezt a mezőt.");
      }
      input.setAttribute("aria-invalid", String(!ok));
      return ok;
    };
    var required = form.querySelectorAll("input[required], textarea[required], select[required], input[type=email]");
    required.forEach(function (input) {
      input.addEventListener("blur", function () { if (input.value) validate(input); });
      input.addEventListener("change", function () { validate(input); });
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var invalid = [];
      required.forEach(function (input) { if (!validate(input)) invalid.push(input); });
      if (invalid.length) { invalid[0].focus(); return; }
      var button = form.querySelector("[type=submit]");
      var label = button.querySelector("[data-label]") || button;
      var data = new FormData(form);

      // A kitöltött adatokból e-mail-vázlat: kész tartalék, ha nincs (vagy nem válaszol) űrlapfogadó.
      var mailto = function () {
        var names = { nev: "Név", ceg: "Cég", beosztas: "Beosztás", email: "E-mail", telefon: "Telefon", hatarido: "Határidő", tema: "Igény", keret: "Keret", megjegyzes: "Megjegyzés" };
        var lines = [];
        Object.keys(names).forEach(function (k) { var v = data.get(k); if (v) lines.push(names[k] + ": " + v); });
        return "mailto:info@rvbcontent.hu?subject=" + encodeURIComponent("Projektindító konzultáció") + "&body=" + encodeURIComponent(lines.join("\n"));
      };
      var showStatus = function (kind) {
        var preview = kind === "preview";
        status.className = "form__status is-visible" + (preview ? " form__status--preview" : "");
        status.setAttribute("role", preview ? "status" : "alert");
        status.innerHTML = "";
        var p = document.createElement("p");
        var b = document.createElement("strong");
        b.textContent = preview ? "Előnézet: az üzenet nem lett elküldve." : "Nem sikerült elküldeni az űrlapot.";
        p.appendChild(b);
        p.appendChild(document.createTextNode(preview
          ? " Ezen a címen az űrlapfogadás nincs bekapcsolva. Küldd el e-mailben a kitöltött adatokkal, vagy hívj minket."
          : " Küldd el e-mailben a kitöltött adatokkal, vagy hívj minket."));
        var actions = document.createElement("div");
        actions.className = "actions";
        var m = document.createElement("a");
        m.className = "link";
        m.href = mailto();
        m.textContent = "E-mail megnyitása a kitöltött adatokkal";
        var t = document.createElement("a");
        t.className = "link";
        t.href = "tel:+36203826638";
        t.textContent = "+36 20 382 6638";
        actions.appendChild(m);
        actions.appendChild(t);
        status.appendChild(p);
        status.appendChild(actions);
        status.focus();
      };
      var reset = function () { button.disabled = false; label.textContent = "Konzultációt kérek"; };

      // Fogadás csak kifejezetten beállított módban: data-form-mode="netlify" (a data-form-hosts
      // listában szereplő éles címen) vagy "endpoint" (data-form-endpoint, JSON {ok:true} válasz).
      // Minden más esetben – helyi előnézet is – semmi nem megy el, és ezt az oldal ki is mondja.
      var mode = form.getAttribute("data-form-mode") || "off";
      var hosts = (form.getAttribute("data-form-hosts") || "").split(",").map(function (h) { return h.trim(); }).filter(Boolean);
      var endpoint = form.getAttribute("data-form-endpoint") || "";
      var live = (mode === "netlify" && hosts.indexOf(window.location.hostname) !== -1) || (mode === "endpoint" && /^https:\/\//.test(endpoint));
      if (!live) { showStatus("preview"); return; }

      button.disabled = true;
      label.textContent = "Küldés…";
      status.className = "form__status";
      var request = mode === "netlify"
        ? fetch("/", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" }, body: new URLSearchParams(data).toString() })
            .then(function (res) { return res.ok; })
        : fetch(endpoint, { method: "POST", headers: { Accept: "application/json" }, body: data })
            .then(function (res) { return res.ok ? res.json().then(function (j) { return j && j.ok === true; }) : false; });
      request
        .then(function (ok) { if (ok) window.location.href = form.getAttribute("action"); else { reset(); showStatus("error"); } })
        .catch(function () { reset(); showStatus("error"); });
    });
  }

  /* ---------- Süti-hozzájárulás ----------
     Mérőkód csak „Elfogadom” után tölthető be; a döntés a reverb:consent eseményen érhető el. */
  var banner = document.querySelector("[data-cookie]");
  var KEY = "rvb-consent";
  var readConsent = function () { try { return localStorage.getItem(KEY); } catch (e) { return null; } };
  var saveConsent = function (v) { try { localStorage.setItem(KEY, v); } catch (e) { /* privát mód */ } };
  if (banner) {
    var current = readConsent();
    if (!current) banner.hidden = false;
    else document.dispatchEvent(new CustomEvent("reverb:consent", { detail: current }));
    banner.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-consent]");
      if (!btn) return;
      var v = btn.getAttribute("data-consent");
      saveConsent(v);
      banner.hidden = true;
      document.dispatchEvent(new CustomEvent("reverb:consent", { detail: v }));
    });
    document.querySelectorAll("[data-cookie-open]").forEach(function (b) {
      b.addEventListener("click", function () {
        banner.hidden = false;
        var first = banner.querySelector("button");
        if (first) first.focus();
      });
    });
  }
})();
