/* TalentConnect — shared + Entertainment feed (TikTok-style interactions) */

(function () {
  'use strict';

  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  }

  function apiUrl(path) {
    return path.startsWith('/') ? path : `/${path}`;
  }

  async function fetchJson(url, options) {
    const opts = Object.assign({ credentials: 'same-origin' }, options || {});
    const headers = Object.assign({}, opts.headers || {});
    if (opts.method && opts.method !== 'GET' && opts.method !== 'HEAD') {
      headers['X-CSRFToken'] = getCsrfToken();
    }
    opts.headers = headers;
    const res = await fetch(apiUrl(url), opts);
    const text = await res.text();
    let data = null;
    try {
      data = text ? JSON.parse(text) : null;
    } catch (e) {
      data = { raw: text };
    }
    if (!res.ok) {
      const err = new Error((data && data.error) || res.statusText || 'Request failed');
      err.status = res.status;
      err.body = data;
      throw err;
    }
    return data;
  }

  /* --- Site nav (mobile menu) — all pages except Entertainment uses .site-nav --- */
  document.querySelectorAll('.nav-menu-toggle').forEach(function (btn) {
    var navId = btn.getAttribute('aria-controls');
    if (!navId) return;
    var nav = document.getElementById(navId);
    if (!nav) return;
    btn.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  window.addEventListener('resize', function () {
    if (window.matchMedia('(min-width: 769px)').matches) {
      document.querySelectorAll('.site-nav.is-open').forEach(function (nav) {
        nav.classList.remove('is-open');
      });
      document.querySelectorAll('.nav-menu-toggle[aria-expanded="true"]').forEach(function (b) {
        b.setAttribute('aria-expanded', 'false');
      });
    }
  });

  /* --- Entertainment feed --- */
  const body = document.body;
  if (!body.classList.contains('Entertainment-page')) {
    return;
  }

  const isAuth = body.getAttribute('data-auth') === '1';
  const loginUrl = body.getAttribute('data-login-url') || '/login/';

  const scrollToId = body.getAttribute('data-scroll-to');
  if (scrollToId) {
    const el = document.getElementById('video-' + scrollToId.trim());
    if (el) {
      requestAnimationFrame(function () {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    }
  }

  const viewedVideos = new Set();

  function updateViewsDisplay(videoId, count) {
    document.querySelectorAll('.views-count[data-video-id="' + videoId + '"]').forEach(function (node) {
      node.textContent = String(count);
    });
  }

  function recordViewOnce(videoId) {
    if (viewedVideos.has(videoId)) {
      return;
    }
    viewedVideos.add(videoId);
    fetchJson('/api/video/' + videoId + '/view/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{}',
    })
      .then(function (data) {
        if (data && typeof data.view_count === 'number') {
          updateViewsDisplay(videoId, data.view_count);
        }
      })
      .catch(function () {
        viewedVideos.delete(videoId);
      });
  }

  /* --- Scroll-synced autoplay (70% visibility), muted, single active clip --- */
  const ACTIVE_VISIBILITY = 0.7;
  const THRESHOLDS = (function () {
    const t = [];
    for (let i = 0; i <= 20; i += 1) {
      t.push(i * 0.05);
    }
    return t;
  })();

  const postRatios = new Map();
  let rafSync = null;
  let lastActiveVideoId = null;

  function syncFeedPlayback() {
    const posts = document.querySelectorAll('.video-post');
    let bestPost = null;
    let bestRatio = 0;
    posts.forEach(function (post) {
      const r = postRatios.get(post) || 0;
      if (r >= ACTIVE_VISIBILITY && r > bestRatio) {
        bestRatio = r;
        bestPost = post;
      }
    });

    if (!bestPost) {
      lastActiveVideoId = null;
    }

    document.querySelectorAll('video.feed-video').forEach(function (v) {
      const post = v.closest('.video-post');
      if (bestPost && post === bestPost) {
        const id = v.getAttribute('data-video-id');
        if (id && id !== lastActiveVideoId) {
          lastActiveVideoId = id;
          recordViewOnce(id);
        }
        const p = v.play();
        if (p && typeof p.catch === 'function') {
          p.catch(function (error) {
            console.log('Autoplay prevented:', error);
            // Try to unmute and play again
            v.muted = false;
            return v.play().catch(function() {});
          });
        }
      } else {
        v.pause();
      }
    });
  }

  function scheduleSyncFeed() {
    if (rafSync !== null) {
      return;
    }
    rafSync = requestAnimationFrame(function () {
      rafSync = null;
      syncFeedPlayback();
    });
  }

  function initScrollAutoplay() {
    const posts = document.querySelectorAll('.video-post');
    if (!posts.length) {
      return;
    }

    posts.forEach(function (post) {
      postRatios.set(post, 0);
    });

    document.querySelectorAll('video.feed-video').forEach(function (v) {
      v.pause();
    });

    if (!('IntersectionObserver' in window)) {
      syncFeedPlayback();
      return;
    }

    const io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          postRatios.set(entry.target, entry.intersectionRatio);
        });
        scheduleSyncFeed();
      },
      {
        root: null,
        rootMargin: '0px',
        threshold: THRESHOLDS,
      }
    );

    posts.forEach(function (post) {
      io.observe(post);
    });

    scheduleSyncFeed();
  }

  initScrollAutoplay();
  initAutoScroll();

  function initAutoScroll() {
    let autoScrollInterval = null;
    let isAutoScrolling = false;
    const scrollDelay = 5000; // 5 seconds per video
    let currentVideoIndex = 0;
    const videos = document.querySelectorAll('.video-post');

    function scrollToNextVideo() {
      if (videos.length === 0) return;
      
      currentVideoIndex = (currentVideoIndex + 1) % videos.length;
      const nextVideo = videos[currentVideoIndex];
      
      if (nextVideo) {
        nextVideo.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }

    function startAutoScroll() {
      if (autoScrollInterval) return;
      isAutoScrolling = true;
      autoScrollInterval = setInterval(scrollToNextVideo, scrollDelay);
    }

    function stopAutoScroll() {
      if (autoScrollInterval) {
        clearInterval(autoScrollInterval);
        autoScrollInterval = null;
      }
      isAutoScrolling = false;
    }

    // Start auto-scroll when page loads
    startAutoScroll();

    // Stop auto-scroll on user interaction
    document.addEventListener('wheel', stopAutoScroll, { passive: true });
    document.addEventListener('touchstart', stopAutoScroll, { passive: true });
    document.addEventListener('keydown', function(e) {
      if (['ArrowUp', 'ArrowDown', 'Home', 'End', 'PageUp', 'PageDown'].includes(e.key)) {
        stopAutoScroll();
      }
    });

    // Resume auto-scroll after 10 seconds of inactivity
    let inactivityTimer;
    function resetInactivityTimer() {
      clearTimeout(inactivityTimer);
      inactivityTimer = setTimeout(startAutoScroll, 10000);
    }

    ['wheel', 'touchstart', 'touchmove', 'keydown'].forEach(event => {
      document.addEventListener(event, resetInactivityTimer, { passive: true });
    });

    resetInactivityTimer();
  }

  /* Likes */
  document.querySelectorAll('.action-like').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const videoId = btn.getAttribute('data-video-id');
      fetchJson('/api/video/' + videoId + '/like/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{}',
      })
        .then(function (data) {
          btn.classList.toggle('is-liked', !!data.liked);
          document.querySelectorAll('.like-count[data-video-id="' + videoId + '"]').forEach(function (node) {
            node.textContent = String(data.like_count);
          });
        })
        .catch(function (err) {
          if (err.status === 401) {
            window.location.href = loginUrl;
          }
        });
    });
  });

  /* Follow — API + localStorage fallback / guest cache */
  const FOLLOW_LS_KEY = 'talentconnect_followed_creator_ids';

  function readFollowIdSet() {
    try {
      const raw = localStorage.getItem(FOLLOW_LS_KEY);
      const arr = raw ? JSON.parse(raw) : [];
      return new Set((Array.isArray(arr) ? arr : []).map(String));
    } catch (e) {
      return new Set();
    }
  }

  function writeFollowIdSet(set) {
    try {
      localStorage.setItem(FOLLOW_LS_KEY, JSON.stringify(Array.from(set)));
    } catch (e) {
      /* ignore quota */
    }
  }

  function applyFollowButtonUI(btn, following) {
    // Add animation trigger
    btn.classList.add('btn-animating');
    setTimeout(function() {
      btn.classList.remove('btn-animating');
    }, 300);
    
    btn.classList.toggle('is-following', following);
    btn.setAttribute('aria-pressed', following ? 'true' : 'false');
    var handle = (btn.getAttribute('data-display-handle') || '').trim();
    var who = handle ? ' ' + handle : ' creator';
    btn.setAttribute('aria-label', (following ? 'Unfollow' : 'Follow') + who);
  }

  var followButtons = document.querySelectorAll('.follow-toggle-btn');
  if (isAuth) {
    var syncSet = readFollowIdSet();
    followButtons.forEach(function (b) {
      var id = b.getAttribute('data-creator-id');
      if (!id) {
        return;
      }
      if (b.classList.contains('is-following')) {
        syncSet.add(String(id));
      } else {
        syncSet.delete(String(id));
      }
    });
    writeFollowIdSet(syncSet);
  } else {
    var guestSet = readFollowIdSet();
    followButtons.forEach(function (b) {
      var id2 = b.getAttribute('data-creator-id');
      if (id2 && guestSet.has(String(id2))) {
        applyFollowButtonUI(b, true);
      }
    });
  }

  followButtons.forEach(function (btn) {
    var cid = btn.getAttribute('data-creator-id');
    if (!cid) {
      return;
    }

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var creatorId = btn.getAttribute('data-creator-id');
      var willFollow = !btn.classList.contains('is-following');

      if (isAuth) {
        fetchJson('/api/user/' + creatorId + '/follow/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: '{}',
        })
          .then(function (data) {
            var on = !!data.following;
            applyFollowButtonUI(btn, on);
            var s = readFollowIdSet();
            if (on) {
              s.add(String(creatorId));
            } else {
              s.delete(String(creatorId));
            }
            writeFollowIdSet(s);
          })
          .catch(function (err) {
            if (err.status === 401) {
              window.location.href = loginUrl;
              return;
            }
            var s = readFollowIdSet();
            if (willFollow) {
              s.add(String(creatorId));
            } else {
              s.delete(String(creatorId));
            }
            writeFollowIdSet(s);
            applyFollowButtonUI(btn, willFollow);
          });
      } else {
        var s2 = readFollowIdSet();
        if (willFollow) {
          s2.add(String(creatorId));
        } else {
          s2.delete(String(creatorId));
        }
        writeFollowIdSet(s2);
        applyFollowButtonUI(btn, willFollow);
      }
    });
  });

  /* Comments modal */
  const commentsModal = document.getElementById('tc-comments-modal');
  const commentsList = document.getElementById('tc-comments-list');
  const commentForm = document.getElementById('tc-comment-form');
  const commentInput = document.getElementById('tc-comment-input');
  const commentLoginHint = document.getElementById('tc-comment-login-hint');
  let activeCommentsVideoId = null;

  function openCommentsModal(videoId) {
    if (!commentsModal || !commentsList) {
      return;
    }
    activeCommentsVideoId = videoId;
    commentsModal.hidden = false;
    commentsList.innerHTML = '<p class="tc-loading">Loading…</p>';
    if (commentForm) {
      commentForm.hidden = false;
    }
    if (commentLoginHint) {
      commentLoginHint.hidden = true;
    }
    fetchJson('/api/video/' + videoId + '/comments/', { method: 'GET' })
      .then(function (data) {
        renderComments(data.comments || []);
      })
      .catch(function () {
        commentsList.innerHTML = '<p class="tc-error">Could not load comments.</p>';
      });
  }

  function renderComments(comments) {
    if (!commentsList) {
      return;
    }
    if (!comments.length) {
      commentsList.innerHTML = '<p class="tc-empty">No comments yet.</p>';
      return;
    }
    commentsList.innerHTML = '';
    comments.forEach(function (c) {
      const row = document.createElement('div');
      row.className = 'tc-comment-row';
      row.innerHTML =
        '<span class="tc-comment-user">' +
        escapeHtml(c.username) +
        '</span>' +
        '<p class="tc-comment-text">' +
        escapeHtml(c.text) +
        '</p>';
      commentsList.appendChild(row);
    });
  }

  function escapeHtml(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function closeCommentsModal() {
    if (!commentsModal) {
      return;
    }
    commentsModal.hidden = true;
    activeCommentsVideoId = null;
  }

  if (commentsModal) {
    commentsModal.querySelectorAll('[data-close-modal]').forEach(function (el) {
      el.addEventListener('click', closeCommentsModal);
    });
  }

  document.querySelectorAll('.action-comment').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const videoId = btn.getAttribute('data-video-id');
      openCommentsModal(videoId);
    });
  });

  if (commentForm && commentInput) {
    commentForm.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!activeCommentsVideoId) {
        return;
      }
      const text = (commentInput.value || '').trim();
      if (!text) {
        return;
      }
      fetchJson('/api/video/' + activeCommentsVideoId + '/comment/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text }),
      })
        .then(function (data) {
          commentInput.value = '';
          if (typeof data.comment_count === 'number') {
            document
              .querySelectorAll('.comment-count[data-video-id="' + activeCommentsVideoId + '"]')
              .forEach(function (node) {
                node.textContent = String(data.comment_count);
              });
          }
          return fetchJson('/api/video/' + activeCommentsVideoId + '/comments/', { method: 'GET' });
        })
        .then(function (d) {
          renderComments((d && d.comments) || []);
        })
        .catch(function (err) {
          // Handle error silently
        });
    });
  }

  /* Share popover */
  const sharePopover = document.getElementById('tc-share-popover');
  let shareVideoId = null;
  let shareAnchorBtn = null;

  function sharePageUrl(videoId) {
    return window.location.origin + '/entertainment/?v=' + encodeURIComponent(videoId);
  }

  function openSharePopover(videoId, anchorBtn) {
    if (!sharePopover) {
      return;
    }
    shareVideoId = videoId;
    shareAnchorBtn = anchorBtn;
    sharePopover.hidden = false;
    const rect = anchorBtn.getBoundingClientRect();
    sharePopover.style.position = 'fixed';
    sharePopover.style.left = Math.max(8, rect.left - 120) + 'px';
    sharePopover.style.top = Math.max(8, rect.top - 140) + 'px';
    sharePopover.style.zIndex = '3000';
  }

  function closeSharePopover() {
    if (!sharePopover) {
      return;
    }
    sharePopover.hidden = true;
    shareVideoId = null;
    shareAnchorBtn = null;
  }

  document.querySelectorAll('.action-share').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      if (sharePopover && !sharePopover.hidden && shareAnchorBtn === btn) {
        closeSharePopover();
        return;
      }
      const videoId = btn.getAttribute('data-video-id');
      openSharePopover(videoId, btn);
    });
  });

  document.addEventListener('click', function () {
    if (sharePopover && !sharePopover.hidden) {
      closeSharePopover();
    }
  });

  if (sharePopover) {
    sharePopover.addEventListener('click', function (e) {
      e.stopPropagation();
    });

    sharePopover.querySelectorAll('.tc-share-item').forEach(function (item) {
      item.addEventListener('click', function () {
        if (!shareVideoId) {
          return;
        }
        const url = sharePageUrl(shareVideoId);
        const kind = item.getAttribute('data-share');
        const text = 'Check out this video on TalentConnect';
        if (kind === 'whatsapp') {
          window.open(
            'https://wa.me/?text=' + encodeURIComponent(text + ' ' + url),
            '_blank'
          );
        } else if (kind === 'facebook') {
          window.open(
            'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url),
            '_blank'
          );
        } else if (kind === 'copy') {
          if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(url).catch(function () {
              window.prompt('Copy link:', url);
            });
          } else {
            window.prompt('Copy link:', url);
          }
        }
        closeSharePopover();
      });
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && commentsModal && !commentsModal.hidden) {
      closeCommentsModal();
    }
  });
})();

