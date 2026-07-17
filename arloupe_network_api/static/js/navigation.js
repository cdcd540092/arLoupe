/* arLoupe 單頁式導覽與本頁重新整理 */

let currentPageName = "arloupe";

document.addEventListener("DOMContentLoaded", () => {
  const pageLinks = document.querySelectorAll("[data-page-target]");
  const pages = document.querySelectorAll("[data-page]");

  /**
   * 顯示指定頁面，其他頁面隱藏。
   */
  window.showPage = function showPage(pageName) {
    const targetPage = document.querySelector(
      `[data-page="${CSS.escape(pageName)}"]`
    );

    if (!targetPage) {
      pageName = "arloupe";
    }

    currentPageName = pageName;
    document.body.dataset.currentPage = pageName;

    pages.forEach((page) => {
      page.classList.toggle(
        "active",
        page.dataset.page === pageName
      );
    });

    pageLinks.forEach((link) => {
      link.classList.toggle(
        "active",
        link.dataset.pageTarget === pageName
      );
    });

    const activePage = document.querySelector(
      `[data-page="${CSS.escape(pageName)}"]`
    );

    if (activePage) {
      const title = activePage.dataset.title || "arLoupe";
      const description = activePage.dataset.description || "";

      const titleEl = document.getElementById("pageTitle");
      const descriptionEl = document.getElementById("pageDescription");

      if (titleEl) titleEl.textContent = title;
      if (descriptionEl) descriptionEl.textContent = description;
    }

    if (window.location.hash !== `#${pageName}`) {
      history.replaceState(null, "", `#${pageName}`);
    }

    // 手機版點選後收合側邊欄
    const sidebar = document.getElementById("sidebar-menu");
    if (
      sidebar &&
      window.innerWidth < 992 &&
      sidebar.classList.contains("show")
    ) {
      sidebar.classList.remove("show");
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  pageLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();

      const pageName = link.dataset.pageTarget;
      if (pageName) {
        window.showPage(pageName);
      }
    });
  });

  const initialPage = window.location.hash.replace("#", "");
  const validPages = Array
    .from(pages)
    .map((page) => page.dataset.page);

  window.showPage(
    validPages.includes(initialPage)
      ? initialPage
      : "arloupe"
  );
});

/**
 * 依目前頁面重新讀取需要的 API。
 */
function refreshCurrentPage() {
  const refreshMap = {
    arloupe: async () => {
      await Promise.allSettled([
        loadCaptureStatus(),
        loadBleStatus()
      ]);
    },

    videos: async () => {
      await loadVideoList(true);
    },

    network: async () => {
      await Promise.allSettled([
        loadStatus(),
        loadJobStatus()
      ]);
    },

    storage: async () => {
      await Promise.allSettled([
        loadStorageStatus(),
        loadCleanupSettings()
      ]);
    },

    settings: async () => {
      await loadCaptureConfig();
    }
  };

  const refresh = refreshMap[currentPageName];

  if (refresh) {
    void refresh();
  }
}
