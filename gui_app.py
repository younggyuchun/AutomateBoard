import customtkinter as ctk
from tkinter import messagebox
import threading
from playwright.sync_api import sync_playwright
from datetime import datetime
import json
from pathlib import Path

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
        self.show_browser_var = ctk.BooleanVar(value=True)

        # 외부영상연결 URL 공유 변수 (주일설교와 팝업창 수정이 동일한 값 공유)
        self.shared_url_var = ctk.StringVar(value="")

        # 로그인 정보 변수 (기본값 설정)
        self.username_var = ctk.StringVar(value="admin48")
        self.password_var = ctk.StringVar(value="tkfkd")

        # 저장된 설정 불러오기
        self.load_settings()

        # 탭 생성
        self.tabview = ctk.CTkTabview(root, corner_radius=15, border_width=2)
        self.tabview.pack(fill='both', expand=True, padx=20, pady=20)

        # 탭 텍스트 크기 설정
        self.tabview._segmented_button.configure(font=("", 16, "bold"))

        # 주일설교 탭
        self.tabview.add("주일설교 등록")
        self.sermon_tab = self.tabview.tab("주일설교 등록")
        self.create_sermon_tab()

        # 팝업 탭
        self.tabview.add("팝업창 수정")
        self.popup_tab = self.tabview.tab("팝업창 수정")
        self.create_popup_tab()

        # 설정 탭
        self.tabview.add("설정")
        self.settings_tab = self.tabview.tab("설정")
        self.create_settings_tab()

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
                print(f"설정 파일이 없습니다. 기본값 사용: {self.config_file}")
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
        """주일설교 등록 탭 생성"""
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
        ctk.CTkLabel(input_frame, text="외부영상연결 URL:", font=("", 16, "bold")).grid(row=4, column=0, sticky='w', padx=15, pady=10)
        self.video_link_entry = ctk.CTkEntry(input_frame, width=500, height=42, corner_radius=10, font=("", 14), textvariable=self.shared_url_var)
        self.video_link_entry.grid(row=4, column=1, pady=10, padx=15)

        # 버튼 프레임 (체크박스와 실행 버튼을 나란히 배치)
        button_frame = ctk.CTkFrame(self.sermon_tab, fg_color="transparent")
        button_frame.pack(pady=15, padx=20, fill='x')

        # 실행 버튼 (오른쪽)
        self.sermon_run_btn = ctk.CTkButton(
            button_frame,
            text="주일설교 등록 실행",
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

    def create_popup_tab(self):
        """팝업창 수정 탭 생성"""
        # 입력 프레임
        input_frame = ctk.CTkFrame(self.popup_tab, corner_radius=15)
        input_frame.pack(fill='x', padx=20, pady=20)

        # URL 입력
        ctk.CTkLabel(input_frame, text="외부영상연결 URL:", font=("", 16, "bold")).grid(row=0, column=0, sticky='w', padx=15, pady=10)
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

    def run_sermon_automation(self):
        """주일설교 등록 자동화 실행"""
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
        self.log_message(self.sermon_log, "주일설교 등록 시작...", self.sermon_progress, 0, self.sermon_progress_label)

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
                    page.goto("https://www.hansomang.ca/_chboard/bbs/board.php?bo_table=m2_1")

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
                    messagebox.showinfo("완료", "주일설교 등록이 완료되었습니다.\n브라우저 창에서 결과를 확인하세요.\n\n확인 후 브라우저를 직접 닫으시면 됩니다.")

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


