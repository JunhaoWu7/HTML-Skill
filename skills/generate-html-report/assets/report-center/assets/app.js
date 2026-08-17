(() => {
  const root = document.documentElement;
  const savedTheme = localStorage.getItem("worklog-theme");
  if (savedTheme) root.dataset.theme = savedTheme;

  document.querySelectorAll(".theme-toggle").forEach((button) => {
    button.addEventListener("click", () => {
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      localStorage.setItem("worklog-theme", next);
    });
  });

  document.querySelector(".print-button")?.addEventListener("click", () => window.print());

  const backTop = document.querySelector(".back-top");
  if (backTop) {
    window.addEventListener("scroll", () => backTop.classList.toggle("visible", window.scrollY > 600), { passive: true });
    backTop.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  }

  const search = document.querySelector("#report-search");
  if (search) {
    search.addEventListener("input", () => {
      const query = search.value.trim().toLocaleLowerCase();
      let visible = 0;
      document.querySelectorAll(".report-card").forEach((card) => {
        const matches = card.textContent.toLocaleLowerCase().includes(query);
        card.hidden = !matches;
        visible += Number(matches);
      });
      document.querySelector("#empty-state").hidden = visible !== 0;
    });
  }

  const year = document.querySelector("#year");
  if (year) year.textContent = new Date().getFullYear();
})();
