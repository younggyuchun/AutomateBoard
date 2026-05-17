import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import re
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont
from openpyxl.styles import Alignment
from datetime import datetime
import json
from pathlib import Path

DEFAULT_NOTICE_URL = "https://www.hansomang.ca/_chboard/bbs/board.php?bo_table=m7_1"

YOUTUBE_CHANNEL_HANDLE = "@Hansomangchurch"
YOUTUBE_LIVE_URL = f"https://www.youtube.com/{YOUTUBE_CHANNEL_HANDLE}/live"

NOTICE_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}

# CustomTkinter 설정
ctk.set_appearance_mode("light")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue" (default), "green", "dark-blue"


class AutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hansomang 자동화 도구")
        self.root.geometry("800x800")

        # 설정 파일 경로 설정
        self.config_file = Path.home() / ".hansomang_automation_config.json"

        # 브라우저 보이기 설정 변수 (True = 보이기, False = 숨기기)
        self.show_browser_var = ctk.BooleanVar(value=False)

        # 외부영상연결 URL 공유 변수 (라이브예배 & 동영상와 팝업창 수정이 동일한 값 공유)
        self.shared_url_var = ctk.StringVar(value="")

        # 로그인 정보 변수 (기본값 설정)
        self.username_var = ctk.StringVar(value="admin48")
        self.password_var = ctk.StringVar(value="tkfkd")

        # 저장된 설정 불러오기
        self.load_settings()

        # 탭 생성 (탭 변경 시 _on_tab_changed 호출)
        self.tabview = ctk.CTkTabview(root, corner_radius=15, border_width=2, command=self._on_tab_changed)
        self.tabview.pack(fill='both', expand=True, padx=20, pady=20)
        # 공지사항 탭 자동 로드 가드
        self.notice_auto_loaded = False

        # 탭 텍스트 크기 설정
        self.tabview._segmented_button.configure(font=("", 16, "bold"))

        # 라이브예배 & 동영상 탭
        self.tabview.add("라이브예배 & 동영상")
        self.sermon_tab = self.tabview.tab("라이브예배 & 동영상")
        self.create_sermon_tab()

        # 팝업 탭
        self.tabview.add("팝업창 수정")
        self.popup_tab = self.tabview.tab("팝업창 수정")
        self.create_popup_tab()

        # 공지사항 추출 탭
        self.tabview.add("공지사항 추출")
        self.notice_tab = self.tabview.tab("공지사항 추출")
        self.notice_items = []  # 파싱된 항목 [(번호, 본문), ...]
        self.notice_list_data = []  # [(제목, URL), ...]
        self.notice_selected_title = ""
        self.create_notice_tab()

        # 설정 탭
        self.tabview.add("설정")
        self.settings_tab = self.tabview.tab("설정")
        self.create_settings_tab()

        # 시작 시 유튜브 URL 자동 입력 + 공지사항 자동 로드(→ 본문 자동 입력)
        self.root.after(300, self.fetch_youtube_live_url)
        self.root.after(500, self._auto_load_notice)

    def _auto_load_notice(self):
        if self.notice_auto_loaded:
            return
        self.notice_auto_loaded = True
        self.load_notice_list()

    def _on_tab_changed(self, _value=None):
        """탭이 바뀌면 호출. 공지사항 탭을 처음 열 때만 자동으로 목록을 불러온다."""
        try:
            current = self.tabview.get()
        except Exception:
            return
        if current == "공지사항 추출" and not self.notice_auto_loaded:
            self.notice_auto_loaded = True
            self.load_notice_list()

    def _enable_copy(self, textbox):
        """텍스트박스에서 macOS Cmd+C/Cmd+A, Ctrl+C/Ctrl+A 로 선택·복사 가능하게 한다."""
        def select_all(_event):
            textbox.tag_add("sel", "1.0", "end-1c")
            textbox.mark_set("insert", "1.0")
            return "break"

        def copy_selection(_event):
            textbox.event_generate("<<Copy>>")
            return "break"

        for seq in ("<Command-c>", "<Command-C>", "<Control-c>", "<Control-C>"):
            textbox.bind(seq, copy_selection)
        for seq in ("<Command-a>", "<Command-A>", "<Control-a>", "<Control-A>"):
            textbox.bind(seq, select_all)

    def load_settings(self):
        """저장된 설정 불러오기"""
        try:
            if self.config_file.exists():
                print(f"설정 파일 발견: {self.config_file}")
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    username = config.get('username', 'admin48')
                    password = config.get('password', 'tkfkd')

                    self.username_var.set(username)
                    self.password_var.set(password)

                    print(f"아이디 로드: {username}")
                    print(f"비밀번호 로드 완료")
            else:
                print(f"설정 파일이 없습니다. 기본값으로 새 파일 생성: {self.config_file}")
                # 설정 파일이 없으면 기본값으로 생성
                config = {
                    'username': 'admin48',
                    'password': 'tkfkd'
                }
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(f"기본 설정 파일 생성 완료")
        except Exception as e:
            print(f"설정 불러오기 실패: {e}")
            import traceback
            traceback.print_exc()

    def save_settings_to_file(self):
        """설정을 파일에 저장"""
        try:
            config = {
                'username': self.username_var.get(),
                'password': self.password_var.get()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"설정 저장 완료: {self.config_file}")
            return True
        except Exception as e:
            print(f"설정 저장 실패: {e}")
            import traceback
            traceback.print_exc()
            return False



    def create_sermon_tab(self):
        """라이브예배 & 동영상 탭 생성"""
        # 입력 프레임
        input_frame = ctk.CTkFrame(self.sermon_tab, corner_radius=15)
        input_frame.pack(fill='x', padx=20, pady=20)

        # 제목 입력
        ctk.CTkLabel(input_frame, text="제목:", font=("", 16, "bold")).grid(row=0, column=0, sticky='w', padx=15, pady=10)
        self.subject_entry = ctk.CTkEntry(input_frame, width=500, height=42, corner_radius=10, font=("", 14))
        self.subject_entry.grid(row=0, column=1, pady=10, padx=15)
        # 기본값 설정: 한소망 교회 주일 설교 + 오늘 날짜
        today = datetime.now().strftime("%Y-%m-%d")
        self.subject_entry.insert(0, f"한소망 교회 주일 설교 {today}")

        # 본문 입력
        ctk.CTkLabel(input_frame, text="본문:", font=("", 16, "bold")).grid(row=1, column=0, sticky='w', padx=15, pady=10)
        self.scripture_entry = ctk.CTkEntry(input_frame, width=500, height=42, corner_radius=10, font=("", 14))
        self.scripture_entry.grid(row=1, column=1, pady=10, padx=15)

        # 설교자 입력
        ctk.CTkLabel(input_frame, text="설교자:", font=("", 16, "bold")).grid(row=2, column=0, sticky='w', padx=15, pady=10)
        self.preacher_entry = ctk.CTkEntry(input_frame, width=500, height=42, corner_radius=10, font=("", 14))
        self.preacher_entry.grid(row=2, column=1, pady=10, padx=15)
        # 기본값 설정
        self.preacher_entry.insert(0, "소성범 목사")

        # 날짜 입력
        ctk.CTkLabel(input_frame, text="날짜:", font=("", 16, "bold")).grid(row=3, column=0, sticky='w', padx=15, pady=10)
        self.date_entry = ctk.CTkEntry(input_frame, width=500, height=42, corner_radius=10, font=("", 14))
        self.date_entry.grid(row=3, column=1, pady=10, padx=15)
        # 기본값 설정: 오늘 날짜 (YYYY-MM-DD 형식)
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today)

        # 영상 URL 입력
        ctk.CTkLabel(input_frame, text="유튜브 URL:", font=("", 16, "bold")).grid(row=4, column=0, sticky='w', padx=15, pady=10)
        self.video_link_entry = ctk.CTkEntry(input_frame, width=500, height=42, corner_radius=10, font=("", 14), textvariable=self.shared_url_var)
        self.video_link_entry.grid(row=4, column=1, pady=10, padx=15)

        # 버튼 프레임 (체크박스와 실행 버튼을 나란히 배치)
        button_frame = ctk.CTkFrame(self.sermon_tab, fg_color="transparent")
        button_frame.pack(pady=15, padx=20, fill='x')

        # 실행 버튼 (오른쪽)
        self.sermon_run_btn = ctk.CTkButton(
            button_frame,
            text="라이브예배 동영상 등록",
            command=self.run_sermon_automation,
            height=50,
            font=("", 17, "bold"),
            corner_radius=12
        )
        self.sermon_run_btn.pack(side='right')

        # 브라우저 보이기 체크박스 (버튼 바로 왼쪽)
        show_browser_checkbox = ctk.CTkCheckBox(
            button_frame,
            text="브라우저 보이기",
            variable=self.show_browser_var,
            font=("", 12),
            corner_radius=6,
            checkbox_width=18,
            checkbox_height=18
        )
        show_browser_checkbox.pack(side='right', padx=(0, 10))

        # 프로그레스 바와 퍼센트 표시
        progress_frame = ctk.CTkFrame(self.sermon_tab, fg_color="transparent")
        progress_frame.pack(fill='x', padx=20, pady=(0, 10))

        self.sermon_progress_label = ctk.CTkLabel(progress_frame, text="0%", font=("", 12))
        self.sermon_progress_label.pack(anchor='e', padx=5, pady=(0, 2))

        self.sermon_progress = ctk.CTkProgressBar(progress_frame, height=20)
        self.sermon_progress.pack(fill='x')
        self.sermon_progress.set(0)

        # 로그 출력
        log_frame = ctk.CTkFrame(self.sermon_tab, corner_radius=15, height=320)
        log_frame.pack(fill='x', padx=20, pady=(0, 20))
        log_frame.pack_propagate(False)  # 프레임 크기 고정

        ctk.CTkLabel(log_frame, text="실행 로그", font=("", 16, "bold"), anchor='w').pack(pady=(10, 5), padx=15, fill='x')

        self.sermon_log = ctk.CTkTextbox(log_frame, font=("Courier", 12), corner_radius=10)
        self.sermon_log.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self._enable_copy(self.sermon_log)

    def create_popup_tab(self):
        """팝업창 수정 탭 생성"""
        # 입력 프레임
        input_frame = ctk.CTkFrame(self.popup_tab, corner_radius=15)
        input_frame.pack(fill='x', padx=20, pady=20)

        # URL 입력
        ctk.CTkLabel(input_frame, text="유튜브 URL:", font=("", 16, "bold")).grid(row=0, column=0, sticky='w', padx=15, pady=10)
        self.popup_url_entry = ctk.CTkEntry(input_frame, width=500, height=42, corner_radius=10, font=("", 14), textvariable=self.shared_url_var)
        self.popup_url_entry.grid(row=0, column=1, pady=15, padx=15)

        # 버튼 프레임 (체크박스와 실행 버튼을 나란히 배치)
        button_frame = ctk.CTkFrame(self.popup_tab, fg_color="transparent")
        button_frame.pack(pady=15, padx=20, fill='x')

        # 실행 버튼 (오른쪽)
        self.popup_run_btn = ctk.CTkButton(
            button_frame,
            text="팝업창 수정 실행",
            command=self.run_popup_automation,
            height=50,
            font=("", 17, "bold"),
            corner_radius=12
        )
        self.popup_run_btn.pack(side='right')

        # 브라우저 보이기 체크박스 (버튼 바로 왼쪽)
        show_browser_checkbox = ctk.CTkCheckBox(
            button_frame,
            text="브라우저 보이기",
            variable=self.show_browser_var,
            font=("", 12),
            corner_radius=6,
            checkbox_width=18,
            checkbox_height=18
        )
        show_browser_checkbox.pack(side='right', padx=(0, 10))

        # 프로그레스 바와 퍼센트 표시
        progress_frame = ctk.CTkFrame(self.popup_tab, fg_color="transparent")
        progress_frame.pack(fill='x', padx=20, pady=(0, 10))

        self.popup_progress_label = ctk.CTkLabel(progress_frame, text="0%", font=("", 12))
        self.popup_progress_label.pack(anchor='e', padx=5, pady=(0, 2))

        self.popup_progress = ctk.CTkProgressBar(progress_frame, height=20)
        self.popup_progress.pack(fill='x')
        self.popup_progress.set(0)

        # 로그 출력
        log_frame = ctk.CTkFrame(self.popup_tab, corner_radius=15, height=320)
        log_frame.pack(fill='x', padx=20, pady=(0, 20))
        log_frame.pack_propagate(False)  # 프레임 크기 고정

        ctk.CTkLabel(log_frame, text="실행 로그", font=("", 16, "bold"), anchor='w').pack(pady=(10, 5), padx=15, fill='x')

        self.popup_log = ctk.CTkTextbox(log_frame, font=("Courier", 12), corner_radius=10)
        self.popup_log.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self._enable_copy(self.popup_log)

    def create_notice_tab(self):
        """공지사항 추출 탭 생성"""
        # URL 입력 프레임
        url_frame = ctk.CTkFrame(self.notice_tab, corner_radius=15)
        url_frame.pack(fill='x', padx=20, pady=(20, 10))
        url_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(url_frame, text="공지사항 URL:", font=("", 16, "bold")).grid(
            row=0, column=0, sticky='w', padx=15, pady=15
        )
        self.notice_url_var = ctk.StringVar(value=DEFAULT_NOTICE_URL)
        self.notice_url_entry = ctk.CTkEntry(
            url_frame, height=42, corner_radius=10, font=("", 14),
            textvariable=self.notice_url_var
        )
        self.notice_url_entry.grid(row=0, column=1, sticky='ew', padx=(0, 10), pady=15)
        self.notice_load_btn = ctk.CTkButton(
            url_frame, text="목록 불러오기", command=self.load_notice_list,
            height=42, font=("", 14, "bold"), corner_radius=10, width=140
        )
        self.notice_load_btn.grid(row=0, column=2, padx=(0, 15), pady=15)

        # 셀렉트 박스 프레임
        select_frame = ctk.CTkFrame(self.notice_tab, corner_radius=15)
        select_frame.pack(fill='x', padx=20, pady=10)
        select_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(select_frame, text="공지사항 선택:", font=("", 16, "bold")).grid(
            row=0, column=0, sticky='w', padx=15, pady=15
        )
        self.notice_select_var = ctk.StringVar(value="")
        self.notice_combobox = ctk.CTkComboBox(
            select_frame, values=["먼저 '목록 불러오기'를 눌러주세요"],
            variable=self.notice_select_var,
            height=42, font=("", 14), corner_radius=10,
            command=self.on_notice_selected, state="readonly"
        )
        self.notice_combobox.grid(row=0, column=1, sticky='ew', padx=(0, 15), pady=15)

        # 프로그레스 바
        progress_frame = ctk.CTkFrame(self.notice_tab, fg_color="transparent")
        progress_frame.pack(fill='x', padx=20, pady=(0, 5))

        self.notice_progress_label = ctk.CTkLabel(progress_frame, text="0%", font=("", 12))
        self.notice_progress_label.pack(anchor='e', padx=5, pady=(0, 2))

        self.notice_progress = ctk.CTkProgressBar(progress_frame, height=20)
        self.notice_progress.pack(fill='x')
        self.notice_progress.set(0)

        # 미리보기 / 로그 프레임
        preview_frame = ctk.CTkFrame(self.notice_tab, corner_radius=15)
        preview_frame.pack(fill='both', expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            preview_frame, text="추출 결과 미리보기",
            font=("", 16, "bold"), anchor='w'
        ).pack(pady=(10, 5), padx=15, fill='x')

        self.notice_preview = ctk.CTkTextbox(preview_frame, font=("", 12), corner_radius=10)
        self.notice_preview.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self._enable_copy(self.notice_preview)

        # 저장 버튼 프레임
        save_frame = ctk.CTkFrame(self.notice_tab, fg_color="transparent")
        save_frame.pack(fill='x', padx=20, pady=(0, 20))

        self.notice_save_btn = ctk.CTkButton(
            save_frame, text="엑셀로 저장", command=self.save_notice_excel,
            height=50, font=("", 17, "bold"), corner_radius=12,
            fg_color="green", hover_color="darkgreen", state="disabled"
        )
        self.notice_save_btn.pack(side='right')

    def _set_notice_progress(self, value, message=None):
        """공지사항 탭 진행 상태 업데이트"""
        self.notice_progress.set(value)
        self.notice_progress_label.configure(text=f"{int(value * 100)}%")
        if message:
            self.notice_preview.insert("end", message + "\n")
            self.notice_preview.see("end")
        self.root.update()

    def _start_sermon_loading(self):
        """라이브예배 탭에 본문 자동 로딩 표시 (placeholder + 진행바 indeterminate)"""
        try:
            self.scripture_entry.delete(0, "end")
            self.scripture_entry.insert(0, "⏳ 본문 자동 불러오는 중...")
            self.sermon_progress.configure(mode="indeterminate")
            self.sermon_progress.start()
            self.sermon_progress_label.configure(text="본문 불러오는 중...")
            self.root.update()
        except Exception:
            pass

    def _stop_sermon_loading(self, clear_placeholder=False):
        """라이브예배 탭의 로딩 표시 해제"""
        try:
            self.sermon_progress.stop()
            self.sermon_progress.configure(mode="determinate")
            self.sermon_progress.set(0)
            self.sermon_progress_label.configure(text="0%")
            if clear_placeholder and self.scripture_entry.get().startswith("⏳"):
                self.scripture_entry.delete(0, "end")
            self.root.update()
        except Exception:
            pass

    def load_notice_list(self):
        """공지사항 목록 페이지에서 제목/링크 불러오기"""
        url = self.notice_url_var.get().strip()
        if not url:
            messagebox.showwarning("입력 오류", "공지사항 URL을 입력해주세요.")
            return

        self.notice_load_btn.configure(state='disabled')
        self.notice_save_btn.configure(state='disabled')
        self.notice_preview.delete("1.0", "end")
        self.notice_items = []
        self.notice_list_data = []
        self.notice_combobox.configure(values=["불러오는 중..."])
        self.notice_select_var.set("불러오는 중...")
        self._set_notice_progress(0.1, f"목록 페이지 요청 중: {url}")
        self._start_sermon_loading()

        def run_task():
            try:
                resp = requests.get(url, headers=NOTICE_REQUEST_HEADERS, timeout=20)
                resp.raise_for_status()
                resp.encoding = resp.apparent_encoding or "utf-8"
                self._set_notice_progress(0.5, "HTML 파싱 중...")

                soup = BeautifulSoup(resp.text, "html.parser")
                # bo_table=...&wr_id=숫자 형태의 글 링크만 추출
                seen = set()
                items = []
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "bo_table=" not in href or "wr_id=" not in href:
                        continue
                    full_url = urljoin(url, href)
                    # 동일 URL 중복 제거
                    if full_url in seen:
                        continue
                    title = a.get_text(strip=True)
                    if not title:
                        continue
                    seen.add(full_url)
                    items.append((title, full_url))

                if not items:
                    self._set_notice_progress(0, "공지사항 링크를 찾을 수 없습니다.")
                    self.notice_combobox.configure(values=["항목 없음"])
                    self.notice_select_var.set("항목 없음")
                    self._stop_sermon_loading(clear_placeholder=True)
                    messagebox.showwarning("결과 없음", "공지사항 링크를 찾을 수 없습니다. URL을 확인해주세요.")
                    return

                self.notice_list_data = items
                titles = [t for t, _ in items]
                self.notice_combobox.configure(values=titles)
                # 자동으로 제일 위에 있는 공지사항 선택 (요구사항 #0)
                self.notice_select_var.set(titles[0])
                self._set_notice_progress(1.0, f"✓ {len(items)}개 공지사항을 찾았습니다. 첫 항목을 자동으로 파싱합니다...")
                # 첫 항목 자동 파싱
                self.on_notice_selected(titles[0])
            except Exception as e:
                self._set_notice_progress(0, f"✗ 목록 불러오기 실패: {e}")
                self._stop_sermon_loading(clear_placeholder=True)
                messagebox.showerror("오류", f"공지사항 목록을 불러오지 못했습니다:\n{e}")
            finally:
                self.notice_load_btn.configure(state='normal')

        threading.Thread(target=run_task, daemon=True).start()

    def on_notice_selected(self, choice):
        """셀렉트박스에서 공지사항 선택 시 본문 파싱"""
        if not choice or choice in ("불러오는 중...", "항목 없음", "먼저 '목록 불러오기'를 눌러주세요"):
            return

        detail_url = None
        for title, link in self.notice_list_data:
            if title == choice:
                detail_url = link
                break
        if not detail_url:
            return

        self.notice_selected_title = choice
        self.notice_save_btn.configure(state='disabled')
        self.notice_preview.delete("1.0", "end")
        self.notice_items = []
        self._set_notice_progress(0.1, f"선택: {choice}\n본문 요청 중: {detail_url}")

        # 라이브예배 탭에도 로딩 표시 — 본문 칸 placeholder + 진행바 indeterminate
        self._start_sermon_loading()

        def run_task():
            try:
                resp = requests.get(detail_url, headers=NOTICE_REQUEST_HEADERS, timeout=20)
                resp.raise_for_status()
                resp.encoding = resp.apparent_encoding or "utf-8"
                self._set_notice_progress(0.5, "본문 파싱 중...")

                items = self.parse_notice_detail(resp.text)
                if not items:
                    self._set_notice_progress(0, "번호가 매겨진 공지 항목을 찾지 못했습니다.")
                    self._stop_sermon_loading(clear_placeholder=True)
                    messagebox.showwarning("파싱 실패", "번호로 시작하는 공지 항목을 찾지 못했습니다.")
                    return

                self.notice_items = items
                self.notice_preview.delete("1.0", "end")
                for num, body in items:
                    self.notice_preview.insert("end", f"━━ {num}번 ━━\n{body}\n\n")
                self.notice_preview.see("1.0")
                self._set_notice_progress(1.0, f"✓ {len(items)}개 항목 파싱 완료. '엑셀로 저장'을 눌러주세요.")
                self.notice_save_btn.configure(state='normal')

                # 성경구절 패턴을 본문에서 찾아 라이브예배 탭의 본문 칸에 채운다
                scripture = self._extract_scripture(resp.text)
                self._stop_sermon_loading(clear_placeholder=True)
                if scripture:
                    self.scripture_entry.delete(0, "end")
                    self.scripture_entry.insert(0, scripture)
                    self.log_message(self.sermon_log, f"✓ 본문 자동 입력: {scripture}")
            except Exception as e:
                self._set_notice_progress(0, f"✗ 본문 파싱 실패: {e}")
                self._stop_sermon_loading(clear_placeholder=True)
                messagebox.showerror("오류", f"공지사항 본문을 불러오지 못했습니다:\n{e}")

        threading.Thread(target=run_task, daemon=True).start()

    def parse_notice_detail(self, html):
        """본문 HTML에서 번호로 시작하는 공지 항목들을 추출"""
        soup = BeautifulSoup(html, "html.parser")
        content = soup.select_one("div.view-content") or soup.select_one("#bo_v_con")
        if not content:
            return []

        # <br>은 줄바꿈으로 변환 (이 컨테이너 안에서만)
        for br in content.find_all("br"):
            br.replace_with("\n")

        # 블록 단위 단락 텍스트 수집. 빈 단락(<p><br></p>)도 그대로 유지해서
        # 번호 항목 사이의 빈 줄을 구분자로 사용한다. 인라인 텍스트는 분리자 없이
        # 이어 붙여 <strong>1</strong><strong>.</strong> 같은 분리 굵게 표기가
        # "1."으로 합쳐지게 한다.
        paragraphs = []
        block_tags = content.find_all(["p", "div", "li"])
        if block_tags:
            for tag in block_tags:
                paragraphs.append(tag.get_text().replace("\xa0", " ").strip())
        else:
            paragraphs = [content.get_text().replace("\xa0", " ").strip()]

        item_start = re.compile(r"^\s*(\d{1,2})\s*[.)、]\s*(.*)$", re.DOTALL)
        items = []
        current_num = None
        current_lines = []
        saw_blank = False

        def flush():
            if current_num is not None:
                body = "\n".join(current_lines).strip()
                # 번호만 있고 제목이 다음 줄로 떨어진 경우 한 줄로 합친다
                # 예: "1.\n주일 환영\n..." → "1. 주일 환영\n..."
                body = re.sub(r"^(\s*\d{1,2}\s*[.)、])\s*\n\s*", r"\1 ", body)
                items.append((current_num, body))

        for para in paragraphs:
            if not para:
                saw_blank = True
                continue
            first_line = para.split("\n", 1)[0].strip()
            m = item_start.match(first_line)
            if m:
                flush()
                current_num = int(m.group(1))
                current_lines = [para.strip()]
                saw_blank = False
                continue
            if current_num is None:
                # 번호 항목이 시작되기 전 텍스트는 무시
                continue
            if saw_blank:
                # 현재 항목 내용이 끝난 뒤(빈 줄) 다음이 번호가 아니면 거기서 중지
                flush()
                current_num = None
                break
            current_lines.append(para.strip())
        flush()

        # 같은 번호로 중복된 항목 정리 (혹시 본문에 동일 번호가 또 등장하면 첫 것만 유지)
        deduped = []
        seen_nums = set()
        for num, body in items:
            if num in seen_nums:
                continue
            seen_nums.add(num)
            deduped.append((num, body))
        deduped.sort(key=lambda x: x[0])
        return deduped

    @staticmethod
    def _extract_scripture(html):
        """본문 HTML에서 성경 구절 패턴을 찾아 반환. 예: '고린도전서 9:24-27'.

        패턴: {한글 책명 2~8자} {장 숫자}:{시작절 숫자}[-{끝절 숫자}]
        '설교' 헤더 뒤에서 먼저 찾고, 없으면 전체 본문에서 첫 매치를 사용.
        """
        soup = BeautifulSoup(html, "html.parser")
        content = soup.select_one("div.view-content") or soup.select_one("#bo_v_con")
        if not content:
            return None
        for br in content.find_all("br"):
            br.replace_with("\n")
        text = content.get_text(separator="\n").replace("\xa0", " ")

        scripture_pat = re.compile(r"([가-힣]{2,8})\s*(\d+):(\d+)(?:\s*-\s*(\d+))?")

        sermon_idx = text.find("설교")
        match = None
        if sermon_idx >= 0:
            match = scripture_pat.search(text, sermon_idx)
        if not match:
            match = scripture_pat.search(text)
        if not match:
            return None

        book, chap, v_start, v_end = match.groups()
        return f"{book} {chap}:{v_start}-{v_end}" if v_end else f"{book} {chap}:{v_start}"

    def save_notice_excel(self):
        """파싱된 항목들을 엑셀로 저장"""
        if not self.notice_items:
            messagebox.showwarning("저장 불가", "저장할 공지 항목이 없습니다. 먼저 공지사항을 선택해주세요.")
            return

        # 파일명 기본값: "VMIX 공지사항 {현재년도}.xlsx"
        default_name = f"VMIX 공지사항 {datetime.now().year}.xlsx"

        file_path = filedialog.asksaveasfilename(
            title="엑셀 파일 저장",
            defaultextension=".xlsx",
            initialfile=default_name,
            filetypes=[("Excel 파일", "*.xlsx"), ("모든 파일", "*.*")]
        )
        if not file_path:
            return

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "공지사항"
            wrap = Alignment(wrap_text=True, vertical="top")
            for idx, (_num, body) in enumerate(self.notice_items, start=1):
                cell = ws.cell(row=idx, column=1, value=self._format_notice_richtext(body))
                cell.alignment = wrap
            ws.column_dimensions["A"].width = 80
            wb.save(file_path)
            messagebox.showinfo("저장 완료", f"엑셀 파일로 저장되었습니다.\n{file_path}")
        except Exception as e:
            messagebox.showerror("저장 실패", f"엑셀 저장 중 오류가 발생했습니다:\n{e}")

    @staticmethod
    def _format_notice_richtext(body):
        """본문을 엑셀 rich text로 변환.

        '1. 주일 / 환영\\n한소망교회...' →
            [BOLD]1. 주일 / 환영[/BOLD]\\n한소망교회...
        개행을 별도 TextBlock으로 빼지 않고 인접 블록에 합쳐서
        Excel이 손상 경고를 띄우지 않도록 한다.
        """
        first_line, _, rest = body.partition("\n")
        m = re.match(r"^\s*(\d+\.)\s*(.*)$", first_line)
        if not m:
            return body
        marker, title = m.group(1), m.group(2).strip()
        bold = InlineFont(b=True)
        plain = InlineFont()
        # 굵게 블록 하나에 "번호 제목" 을 한 줄로 담는다
        bold_text = f"{marker} {title}" if title else marker
        parts = [TextBlock(bold, bold_text)]
        if rest:
            # 제목 줄과 본문 사이에 빈 줄 한 줄을 추가해 가독성 확보
            parts.append(TextBlock(plain, "\n\n" + rest))
        return CellRichText(parts)

    def create_settings_tab(self):
        """설정 탭 생성"""
        # 설명 프레임
        info_frame = ctk.CTkFrame(self.settings_tab, corner_radius=15)
        info_frame.pack(fill='x', padx=20, pady=20)

        info_label = ctk.CTkLabel(
            info_frame,
            text="로그인 정보 설정\n아이디와 비밀번호를 입력하고 저장하면 다음 실행 시에도 유지됩니다.",
            font=("", 14),
            justify="left"
        )
        info_label.pack(padx=20, pady=20)

        # 입력 프레임
        input_frame = ctk.CTkFrame(self.settings_tab, corner_radius=15)
        input_frame.pack(fill='x', padx=20, pady=20)

        # 아이디 입력
        ctk.CTkLabel(input_frame, text="아이디:", font=("", 16, "bold")).grid(row=0, column=0, sticky='w', padx=15, pady=15)
        self.settings_username_entry = ctk.CTkEntry(
            input_frame,
            width=500,
            height=42,
            corner_radius=10,
            font=("", 14),
            textvariable=self.username_var
        )
        self.settings_username_entry.grid(row=0, column=1, pady=15, padx=15)

        # 비밀번호 입력 (마스킹 처리)
        ctk.CTkLabel(input_frame, text="비밀번호:", font=("", 16, "bold")).grid(row=1, column=0, sticky='w', padx=15, pady=15)
        self.settings_password_entry = ctk.CTkEntry(
            input_frame,
            width=500,
            height=42,
            corner_radius=10,
            font=("", 14),
            textvariable=self.password_var,
            show="●"  # 비밀번호 마스킹 처리
        )
        self.settings_password_entry.grid(row=1, column=1, pady=15, padx=15)

        # 저장 버튼
        save_button_frame = ctk.CTkFrame(self.settings_tab, fg_color="transparent")
        save_button_frame.pack(pady=15, padx=20, fill='x')

        self.settings_save_btn = ctk.CTkButton(
            save_button_frame,
            text="설정 저장",
            command=self.save_settings,
            height=50,
            font=("", 17, "bold"),
            corner_radius=12,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.settings_save_btn.pack(side='right')

        # 상태 메시지
        self.settings_status_label = ctk.CTkLabel(
            self.settings_tab,
            text="",
            font=("", 14),
            text_color="green"
        )
        self.settings_status_label.pack(pady=10)

    def save_settings(self):
        """설정 저장"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("입력 오류", "아이디와 비밀번호를 모두 입력해주세요.")
            return

        # 파일에 저장
        if self.save_settings_to_file():
            self.settings_status_label.configure(text="✓ 설정이 저장되었습니다.")
            messagebox.showinfo("완료", "설정이 저장되었습니다.")
        else:
            self.settings_status_label.configure(text="✗ 설정 저장 실패", text_color="red")
            messagebox.showerror("오류", "설정 저장에 실패했습니다.")

    def log_message(self, log_widget, message, progress_bar=None, progress_value=None, progress_label=None, color=None):
        """로그 메시지 출력 및 프로그레스 바 업데이트"""
        if color:
            # 색상이 지정된 경우 태그를 사용하여 색상 적용
            tag_name = f"color_{color}"
            log_widget.tag_config(tag_name, foreground=color)
            log_widget.insert("end", message + '\n', tag_name)
        else:
            log_widget.insert("end", message + '\n')
        log_widget.see("end")
        if progress_bar is not None and progress_value is not None:
            progress_bar.set(progress_value)
            if progress_label is not None:
                progress_label.configure(text=f"{int(progress_value * 100)}%")
        self.root.update()

    def fetch_youtube_live_url(self):
        """YouTube 채널의 라이브 URL을 유튜브 URL 칸에 그대로 채운다."""
        self.shared_url_var.set(YOUTUBE_LIVE_URL)
        self.log_message(self.sermon_log, f"✓ 유튜브 URL 자동 입력: {YOUTUBE_LIVE_URL}")

    def run_sermon_automation(self):
        """라이브예배 & 동영상 자동화 실행"""
        # 아이디/비밀번호 검증
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("로그인 정보 오류", "설정 탭에서 아이디와 비밀번호를 입력해주세요.")
            return

        # 입력 값 검증
        subject = self.subject_entry.get().strip()
        scripture = self.scripture_entry.get().strip()
        preacher = self.preacher_entry.get().strip()
        date = self.date_entry.get().strip()
        video_link = self.video_link_entry.get().strip()

        if not all([subject, scripture, preacher, date, video_link]):
            messagebox.showwarning("입력 오류", "모든 필드를 입력해주세요.")
            return

        # 버튼 비활성화
        self.sermon_run_btn.configure(state='disabled')
        self.sermon_log.delete("1.0", "end")
        self.sermon_progress.set(0)
        self.sermon_progress_label.configure(text="0%")
        self.log_message(self.sermon_log, "라이브예배 & 동영상 시작...", self.sermon_progress, 0, self.sermon_progress_label)

        def run_task():
            try:
                with sync_playwright() as playwright:
                    self.log_message(self.sermon_log, "브라우저 실행 중...", self.sermon_progress, 0.1, self.sermon_progress_label)
                    browser = playwright.chromium.launch(
                        headless=not self.show_browser_var.get(),
                        channel="chrome"  # 시스템에 설치된 크롬을 직접 사용
                    )
                    context = browser.new_context()
                    page = context.new_page()

                    self.log_message(self.sermon_log, "웹사이트 접속 중...", self.sermon_progress, 0.2, self.sermon_progress_label)
                    page.goto("https://www.hansomang.ca/", wait_until="domcontentloaded")

                    self.log_message(self.sermon_log, "로그인 중...", self.sermon_progress, 0.3, self.sermon_progress_label)
                    page.get_by_role("link", name="로그인", exact=True).click()
                    page.wait_for_load_state("domcontentloaded")
                    page.locator(".col-12").first.click()
                    page.wait_for_load_state("domcontentloaded")
                    page.get_by_role("textbox", name="아이디").click()

                    # 로그인 정보 로그 출력
                    login_username = self.username_var.get()
                    login_password = self.password_var.get()
                    print(f"로그인 시도 - 아이디: {login_username}, 비밀번호 길이: {len(login_password)}")

                    page.get_by_role("textbox", name="아이디").fill(login_username)
                    page.get_by_role("textbox", name="아이디").press("Tab")
                    page.get_by_role("textbox", name="비밀번호").fill(login_password)
                    page.get_by_role("button", name=" 로그인").click()
                    page.wait_for_load_state("domcontentloaded")

                    # 로그인 성공 여부 확인
                    self.log_message(self.sermon_log, "로그인 결과 확인 중...", self.sermon_progress, 0.4, self.sermon_progress_label)
                    try:
                        # 로그인 성공 시 나타나는 요소 확인 (로그아웃 링크 또는 관리자 메뉴)
                        page.wait_for_selector("text=로그아웃", timeout=5000)
                        self.log_message(self.sermon_log, "✓ 로그인 성공!", self.sermon_progress, 0.45, self.sermon_progress_label)
                    except:
                        # 로그인 실패
                        self.log_message(self.sermon_log, "✗ 로그인 실패: 아이디 또는 비밀번호를 확인해주세요.", self.sermon_progress, 0.4, self.sermon_progress_label, color="red")
                        messagebox.showerror("로그인 실패", "아이디 또는 비밀번호가 올바르지 않습니다.\n설정 탭에서 로그인 정보를 확인해주세요.")
                        context.close()
                        browser.close()
                        return

                    self.log_message(self.sermon_log, "주일설교 페이지 이동 중...", self.sermon_progress, 0.5, self.sermon_progress_label)
                    page.goto("https://www.hansomang.ca/_chboard/bbs/board.php?bo_table=m2_3")

                    self.log_message(self.sermon_log, "글쓰기 페이지 로딩 중...", self.sermon_progress, 0.6, self.sermon_progress_label)
                    page.get_by_role("link", name=" 글쓰기").click()
                    page.wait_for_load_state("domcontentloaded")

                    self.log_message(self.sermon_log, "데이터 입력 중...", self.sermon_progress, 0.7, self.sermon_progress_label)
                    page.locator("#wr_subject").click()
                    page.locator("#wr_subject").fill(subject)
                    page.locator("input[name=\"wr_7\"]").click()
                    page.locator("input[name=\"wr_7\"]").fill(scripture)
                    page.locator("input[name=\"wr_8\"]").click()
                    page.locator("input[name=\"wr_8\"]").fill(preacher)

                    # 날짜 입력
                    page.locator("input[name=\"wr_9\"]").click()
                    # 달력을 끄기 위해 다른 곳 클릭
                    page.locator("#wr_subject").click()
                    # 입력된 날짜를 YYYY-MM-DD 형식으로 입력
                    page.locator("input[name=\"wr_9\"]").click()
                    page.locator("input[name=\"wr_9\"]").fill(date)

                    page.locator("input[name=\"wr_link1\"]").click()
                    page.locator("input[name=\"wr_link1\"]").fill(video_link)

                    self.log_message(self.sermon_log, "글 등록 중...", self.sermon_progress, 0.85, self.sermon_progress_label)
                    page.get_by_role("button", name="글쓰기완료").click()
                    page.wait_for_load_state("domcontentloaded")

                    self.log_message(self.sermon_log, "완료! 결과를 확인하세요.", self.sermon_progress, 1.0, self.sermon_progress_label)
                    messagebox.showinfo("완료", "라이브예배 & 동영상 등록이 완료되었습니다.\n브라우저 창에서 결과를 확인하세요.\n\n확인 후 브라우저를 직접 닫으시면 됩니다.")

                    # 브라우저를 닫지 않음 - 사용자가 수동으로 닫을 수 있도록 유지

            except Exception as e:
                self.log_message(self.sermon_log, f"✗ 오류 발생: {str(e)}", color="red")
                messagebox.showerror("오류", f"실행 중 오류가 발생했습니다:\n{str(e)}")
            finally:
                self.sermon_run_btn.configure(state='normal')

        # 별도 스레드에서 실행
        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()

    def run_popup_automation(self):
        """팝업창 수정 자동화 실행"""
        # 아이디/비밀번호 검증
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("로그인 정보 오류", "설정 탭에서 아이디와 비밀번호를 입력해주세요.")
            return

        # 입력 값 검증
        popup_url = self.popup_url_entry.get().strip()

        if not popup_url:
            messagebox.showwarning("입력 오류", "팝업 URL을 입력해주세요.")
            return

        # 버튼 비활성화
        self.popup_run_btn.configure(state='disabled')
        self.popup_log.delete("1.0", "end")
        self.popup_progress.set(0)
        self.popup_progress_label.configure(text="0%")
        self.log_message(self.popup_log, "팝업창 수정 시작...", self.popup_progress, 0, self.popup_progress_label)

        def run_task():
            try:
                with sync_playwright() as playwright:
                    self.log_message(self.popup_log, "브라우저 실행 중...", self.popup_progress, 0.1, self.popup_progress_label)
                    browser = playwright.chromium.launch(
                        headless=not self.show_browser_var.get(),
                        channel="chrome"  # 시스템에 설치된 크롬을 직접 사용
                    )
                    context = browser.new_context()
                    page = context.new_page()

                    self.log_message(self.popup_log, "웹사이트 접속 중...", self.popup_progress, 0.2, self.popup_progress_label)
                    page.goto("https://www.hansomang.ca/", wait_until="domcontentloaded")

                    self.log_message(self.popup_log, "로그인 중...", self.popup_progress, 0.3, self.popup_progress_label)
                    page.get_by_role("link", name="로그인", exact=True).click()
                    page.wait_for_load_state("domcontentloaded")
                    page.locator(".col-12").first.click()
                    page.wait_for_load_state("domcontentloaded")
                    page.get_by_role("textbox", name="아이디").click()

                    # 로그인 정보 로그 출력
                    login_username = self.username_var.get()
                    login_password = self.password_var.get()
                    print(f"로그인 시도 - 아이디: {login_username}, 비밀번호 길이: {len(login_password)}")

                    page.get_by_role("textbox", name="아이디").fill(login_username)
                    page.get_by_role("textbox", name="아이디").press("Tab")
                    page.get_by_role("textbox", name="비밀번호").fill(login_password)
                    page.get_by_role("button", name=" 로그인").click()
                    page.wait_for_load_state("domcontentloaded")

                    # 로그인 성공 여부 확인
                    self.log_message(self.popup_log, "로그인 결과 확인 중...", self.popup_progress, 0.4, self.popup_progress_label)
                    try:
                        # 로그인 성공 시 나타나는 요소 확인 (로그아웃 링크 또는 관리자 메뉴)
                        page.wait_for_selector("text=로그아웃", timeout=5000)
                        self.log_message(self.popup_log, "✓ 로그인 성공!", self.popup_progress, 0.45, self.popup_progress_label)
                    except:
                        # 로그인 실패
                        self.log_message(self.popup_log, "✗ 로그인 실패: 아이디 또는 비밀번호를 확인해주세요.", self.popup_progress, 0.4, self.popup_progress_label, color="red")
                        messagebox.showerror("로그인 실패", "아이디 또는 비밀번호가 올바르지 않습니다.\n설정 탭에서 로그인 정보를 확인해주세요.")
                        context.close()
                        browser.close()
                        return

                    self.log_message(self.popup_log, "관리자 페이지 이동 중...", self.popup_progress, 0.5, self.popup_progress_label)
                    page.get_by_role("link", name="관리자").click()
                    page.wait_for_load_state("domcontentloaded")
                    page.locator("a").filter(has_text="웹사이트 관리").click()
                    page.wait_for_load_state("domcontentloaded")
                    page.get_by_role("link", name="팝업창").click()
                    page.wait_for_load_state("domcontentloaded")

                    self.log_message(self.popup_log, "팝업창 수정 중...", self.popup_progress, 0.7, self.popup_progress_label)
                    page.get_by_role("link", name="수정").nth(3).click()
                    page.get_by_text("클릭").nth(3).click()
                    page.wait_for_load_state("domcontentloaded")
                    page.get_by_role("button", name="편집 링크").click()
                    page.wait_for_load_state("domcontentloaded")
                    page.get_by_role("textbox", name="URL").click()
                    page.get_by_role("textbox", name="URL").press("ControlOrMeta+a")
                    page.get_by_role("textbox", name="URL").fill(popup_url)
                    page.get_by_role("button", name="업데이트").click()
                    page.get_by_role("button", name=" 팝업창수정완료").click()
                    page.wait_for_load_state("domcontentloaded")

                    self.log_message(self.popup_log, "완료! 브라우저 종료 중...", self.popup_progress, 0.95, self.popup_progress_label)
                    context.close()
                    browser.close()

                    self.log_message(self.popup_log, "✓ 팝업창 수정이 완료되었습니다.", self.popup_progress, 1.0, self.popup_progress_label)
                    messagebox.showinfo("완료", "팝업창 수정이 완료되었습니다.")

            except Exception as e:
                self.log_message(self.popup_log, f"✗ 오류 발생: {str(e)}", color="red")
                messagebox.showerror("오류", f"실행 중 오류가 발생했습니다:\n{str(e)}")
            finally:
                self.popup_run_btn.configure(state='normal')

        # 별도 스레드에서 실행
        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()


def main():
    root = ctk.CTk()
    app = AutomationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()



