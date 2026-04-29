import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from conftest import FRONTEND_URL, navigate_to_call


class TestLanguageSelectorUI:
    """Visual and interactive checks for the LanguageSelector page."""

    def test_title_text(self, browser, frontend_service):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        title = browser.find_element(By.CLASS_NAME, "ls-title")
        assert "Meeting Translator" in title.text

    def test_subtitle_text(self, browser, frontend_service):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        subtitle = browser.find_element(By.CLASS_NAME, "ls-subtitle")
        assert subtitle.is_displayed()
        assert len(subtitle.text) > 0

    def test_card_is_visible(self, browser, frontend_service):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        card = browser.find_element(By.CLASS_NAME, "ls-card")
        assert card.is_displayed()

    def test_all_language_items_have_flags(self, browser, frontend_service):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        flags = browser.find_elements(By.CLASS_NAME, "ls-flag")
        assert len(flags) >= 3
        for flag in flags:
            assert flag.text.strip() != "", "Flag emoji should not be empty"

    def test_all_language_items_have_names(self, browser, frontend_service):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        names = browser.find_elements(By.CLASS_NAME, "ls-name")
        for name in names:
            assert name.text.strip() != "", "Language name should not be empty"

    def test_selected_item_shows_check(self, browser, frontend_service):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        # At least one item should already be selected on load
        selected = browser.find_elements(By.CLASS_NAME, "ls-item--selected")
        assert len(selected) >= 1
        check = selected[0].find_element(By.CLASS_NAME, "ls-check")
        assert check.is_displayed()

    def test_clicking_item_changes_selection(self, browser, frontend_service):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        items = browser.find_elements(By.CLASS_NAME, "ls-item")
        # Click the second item
        items[1].click()
        time.sleep(0.3)
        assert "ls-item--selected" in items[1].get_attribute("class")

    def test_only_one_item_selected_at_a_time(self, browser, frontend_service):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        items = browser.find_elements(By.CLASS_NAME, "ls-item")
        items[0].click()
        time.sleep(0.2)
        items[1].click()
        time.sleep(0.2)
        selected = browser.find_elements(By.CLASS_NAME, "ls-item--selected")
        assert len(selected) == 1, "Only one language should be selected at a time"

    def test_next_button_text(self, browser, frontend_service):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        btn = browser.find_element(By.CLASS_NAME, "ls-btn-primary")
        assert btn.text.strip() != ""


class TestSpeakerProfileUI:
    """Visual and interactive checks for the SpeakerProfile page."""

    def _go_to_profile(self, browser, wait):
        browser.get(FRONTEND_URL)
        time.sleep(2)
        browser.find_element(By.CLASS_NAME, "ls-btn-primary").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "sp-page")))

    def test_title_present(self, browser, frontend_service, wait):
        self._go_to_profile(browser, wait)
        assert browser.find_element(By.CLASS_NAME, "sp-title").is_displayed()

    def test_name_input_placeholder(self, browser, frontend_service, wait):
        self._go_to_profile(browser, wait)
        name_input = browser.find_element(By.CLASS_NAME, "sp-input")
        assert name_input.is_displayed()
        assert name_input.is_enabled()

    def test_url_input_placeholder(self, browser, frontend_service, wait):
        self._go_to_profile(browser, wait)
        url_input = browser.find_element(By.CLASS_NAME, "sp-url-input")
        assert url_input.is_displayed()
        assert url_input.is_enabled()

    def test_add_button_displayed(self, browser, frontend_service, wait):
        self._go_to_profile(browser, wait)
        add_btn = browser.find_element(By.CLASS_NAME, "sp-btn-add")
        assert add_btn.is_displayed()

    def test_skip_button_displayed(self, browser, frontend_service, wait):
        self._go_to_profile(browser, wait)
        skip_btn = browser.find_element(By.CLASS_NAME, "sp-btn-skip")
        assert skip_btn.is_displayed()

    def test_name_input_is_focusable(self, browser, frontend_service, wait):
        self._go_to_profile(browser, wait)
        name_input = browser.find_element(By.CLASS_NAME, "sp-input")
        name_input.click()
        active = browser.switch_to.active_element
        assert active == name_input

    def test_analyze_button_displayed(self, browser, frontend_service, wait):
        self._go_to_profile(browser, wait)
        analyze_btn = browser.find_element(By.CLASS_NAME, "sp-btn-primary")
        assert analyze_btn.is_displayed()


class TestCallOverlayUI:
    """Visual checks for the CallOverlay page."""

    def test_top_bar_displayed(self, browser, frontend_service, wait):
        navigate_to_call(browser)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-bar")))
        bar = browser.find_element(By.CLASS_NAME, "co-bar")
        assert bar.is_displayed()

    def test_flag_emoji_displayed(self, browser, frontend_service, wait):
        navigate_to_call(browser)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-flag")))
        flag = browser.find_element(By.CLASS_NAME, "co-flag")
        assert flag.is_displayed()
        assert flag.text.strip() != ""

    def test_caption_area_displayed(self, browser, frontend_service, wait):
        navigate_to_call(browser)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-caption")))
        caption = browser.find_element(By.CLASS_NAME, "co-caption")
        assert caption.is_displayed()

    def test_exit_button_displayed(self, browser, frontend_service, wait):
        navigate_to_call(browser)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-exit-btn")))
        exit_btn = browser.find_element(By.CLASS_NAME, "co-exit-btn")
        assert exit_btn.is_displayed()

    def test_stats_line_displayed(self, browser, frontend_service, wait):
        navigate_to_call(browser)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-stats")))
        stats = browser.find_element(By.CLASS_NAME, "co-stats")
        assert stats.is_displayed()

    def test_connection_dot_displayed(self, browser, frontend_service, wait):
        navigate_to_call(browser)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-dot")))
        dot = browser.find_element(By.CLASS_NAME, "co-dot")
        assert dot.is_displayed()

    def test_exit_modal_has_two_buttons(self, browser, frontend_service, wait):
        navigate_to_call(browser)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-exit-btn")))
        browser.find_element(By.CLASS_NAME, "co-exit-btn").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-modal")))
        continue_btn = browser.find_element(By.CLASS_NAME, "co-modal-continue")
        end_btn = browser.find_element(By.CLASS_NAME, "co-modal-end")
        assert continue_btn.is_displayed()
        assert end_btn.is_displayed()


class TestSessionSummaryUI:
    """Visual checks for the SessionSummary page."""

    def _go_to_summary(self, browser, wait):
        navigate_to_call(browser)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-exit-btn")))
        browser.find_element(By.CLASS_NAME, "co-exit-btn").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "co-modal-end")))
        browser.find_element(By.CLASS_NAME, "co-modal-end").click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ss-page")))

    def test_summary_card_displayed(self, browser, frontend_service, wait):
        self._go_to_summary(browser, wait)
        card = browser.find_element(By.CLASS_NAME, "ss-card")
        assert card.is_displayed()

    def test_summary_title_displayed(self, browser, frontend_service, wait):
        self._go_to_summary(browser, wait)
        title = browser.find_element(By.CLASS_NAME, "ss-title")
        assert title.is_displayed()
        assert "Resumo" in title.text

    def test_stats_grid_has_three_items(self, browser, frontend_service, wait):
        self._go_to_summary(browser, wait)
        stats = browser.find_elements(By.CLASS_NAME, "ss-stat")
        assert len(stats) >= 3

    def test_stat_values_displayed(self, browser, frontend_service, wait):
        self._go_to_summary(browser, wait)
        values = browser.find_elements(By.CLASS_NAME, "ss-stat-value")
        for val in values:
            assert val.is_displayed()

    def test_stat_labels_displayed(self, browser, frontend_service, wait):
        self._go_to_summary(browser, wait)
        labels = browser.find_elements(By.CLASS_NAME, "ss-stat-label")
        for label in labels:
            assert label.is_displayed()
            assert label.text.strip() != ""

    def test_phrases_section_conditional(self, browser, frontend_service, wait):
        # ss-phrases only renders when recent_phrases.length > 0 — no audio in tests
        self._go_to_summary(browser, wait)
        sections = browser.find_elements(By.CLASS_NAME, "ss-phrases")
        if sections:
            assert sections[0].is_displayed()

    def test_new_session_button_displayed(self, browser, frontend_service, wait):
        self._go_to_summary(browser, wait)
        btn = browser.find_element(By.CLASS_NAME, "ss-btn-primary")
        assert btn.is_displayed()
        assert btn.is_enabled()
        assert btn.text.strip() != ""
