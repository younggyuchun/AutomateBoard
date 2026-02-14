import customtkinter as ctk
from tkinter import messagebox
import threading
from playwright.sync_api import sync_playwright
from datetime import datetime

# CustomTkinter 설정
ctk.set_appearance_mode("light")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue" (default), "green", "dark-blue"


class AutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hansomang 자동화 도구")
        self.root.geometry("800x700")

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
        self.video_link_entry = ctk.CTkEntry(input_frame, width=500, height=42, corner_radius=10, font=("", 14))
        self.video_link_entry.grid(row=4, column=1, pady=10, padx=15)

        # 실행 버튼
        self.sermon_run_btn = ctk.CTkButton(
            self.sermon_tab,
            text="주일설교 등록 실행",
            command=self.run_sermon_automation,
            height=50,
            font=("", 17, "bold"),
            corner_radius=12
        )
        self.sermon_run_btn.pack(pady=15)

        # 로그 출력
        log_frame = ctk.CTkFrame(self.sermon_tab, corner_radius=15)
        log_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(log_frame, text="실행 로그", font=("", 16, "bold"), anchor='w').pack(pady=(10, 5), padx=15, fill='x')

        self.sermon_log = ctk.CTkTextbox(log_frame, height=200, font=("Courier", 12), corner_radius=10)
        self.sermon_log.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def create_popup_tab(self):
        """팝업창 수정 탭 생성"""
        # 입력 프레임
        input_frame = ctk.CTkFrame(self.popup_tab, corner_radius=15)
        input_frame.pack(fill='x', padx=20, pady=20)

        # URL 입력
        ctk.CTkLabel(input_frame, text="팝업 URL:", font=("", 16, "bold")).grid(row=0, column=0, sticky='w', padx=15, pady=15)
        self.popup_url_entry = ctk.CTkEntry(input_frame, width=550, height=42, corner_radius=10, font=("", 14))
        self.popup_url_entry.grid(row=0, column=1, pady=15, padx=15)

        # 실행 버튼
        self.popup_run_btn = ctk.CTkButton(
            self.popup_tab,
            text="팝업창 수정 실행",
            command=self.run_popup_automation,
            height=50,
            font=("", 17, "bold"),
            corner_radius=12
        )
        self.popup_run_btn.pack(pady=15)

        # 로그 출력
        log_frame = ctk.CTkFrame(self.popup_tab, corner_radius=15)
        log_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(log_frame, text="실행 로그", font=("", 16, "bold"), anchor='w').pack(pady=(10, 5), padx=15, fill='x')

        self.popup_log = ctk.CTkTextbox(log_frame, height=300, font=("Courier", 12), corner_radius=10)
        self.popup_log.pack(fill='both', expand=True, padx=10, pady=(0, 10))

    def log_message(self, log_widget, message):
        """로그 메시지 출력"""
        log_widget.insert("end", message + '\n')
        log_widget.see("end")
        self.root.update()

    def run_sermon_automation(self):
        """주일설교 등록 자동화 실행"""
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
        self.log_message(self.sermon_log, "주일설교 등록 시작...")

        def run_task():
            try:
                with sync_playwright() as playwright:
                    self.log_message(self.sermon_log, "브라우저 실행 중...")
                    #browser = playwright.chromium.launch(headless=False)
                    browser = playwright.chromium.launch(
                        headless=True,
                        channel="chrome"  # 시스템에 설치된 크롬을 직접 사용
                    )
                    context = browser.new_context()
                    page = context.new_page()

                    self.log_message(self.sermon_log, "웹사이트 접속 중...")
                    page.goto("https://www.hansomang.ca/", wait_until="domcontentloaded")

                    self.log_message(self.sermon_log, "로그인 중...")
                    page.get_by_role("link", name="로그인", exact=True).click()
                    page.wait_for_load_state("domcontentloaded")
                    page.locator(".col-12").first.click()
                    page.wait_for_load_state("domcontentloaded")
                    page.get_by_role("textbox", name="아이디").click()
                    page.get_by_role("textbox", name="아이디").fill("admin48")
                    page.get_by_role("textbox", name="아이디").press("Tab")
                    page.get_by_role("textbox", name="비밀번호").fill("tkfkd")
                    page.get_by_role("button", name=" 로그인").click()
                    page.wait_for_load_state("domcontentloaded")

                    self.log_message(self.sermon_log, "주일설교 페이지 이동 중...")
                    page.goto("https://www.hansomang.ca/_chboard/bbs/board.php?bo_table=m2_1")

                    self.log_message(self.sermon_log, "글쓰기 페이지 로딩 중...")
                    page.get_by_role("link", name=" 글쓰기").click()
                    page.wait_for_load_state("domcontentloaded")

                    self.log_message(self.sermon_log, "데이터 입력 중...")
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

                    self.log_message(self.sermon_log, "글 등록 중...")
                    page.get_by_role("button", name="글쓰기완료").click()
                    page.wait_for_load_state("domcontentloaded")

                    self.log_message(self.sermon_log, "완료! 브라우저 종료 중...")
                    context.close()
                    browser.close()

                    self.log_message(self.sermon_log, "✓ 주일설교 등록이 완료되었습니다.")
                    messagebox.showinfo("완료", "주일설교 등록이 완료되었습니다.")

            except Exception as e:
                self.log_message(self.sermon_log, f"✗ 오류 발생: {str(e)}")
                messagebox.showerror("오류", f"실행 중 오류가 발생했습니다:\n{str(e)}")
            finally:
                self.sermon_run_btn.configure(state='normal')

        # 별도 스레드에서 실행
        thread = threading.Thread(target=run_task, daemon=True)
        thread.start()

    def run_popup_automation(self):
        """팝업창 수정 자동화 실행"""
        # 입력 값 검증
        popup_url = self.popup_url_entry.get().strip()

        if not popup_url:
            messagebox.showwarning("입력 오류", "팝업 URL을 입력해주세요.")
            return

        # 버튼 비활성화
        self.popup_run_btn.configure(state='disabled')
        self.popup_log.delete("1.0", "end")
        self.log_message(self.popup_log, "팝업창 수정 시작...")

        def run_task():
            try:
                with sync_playwright() as playwright:
                    self.log_message(self.popup_log, "브라우저 실행 중...")
                    browser = playwright.chromium.launch(headless=False)
                    context = browser.new_context()
                    page = context.new_page()

                    self.log_message(self.popup_log, "웹사이트 접속 중...")
                    page.goto("https://www.hansomang.ca/", wait_until="domcontentloaded")

                    self.log_message(self.popup_log, "로그인 중...")
                    page.get_by_role("link", name="로그인", exact=True).click()
                    page.wait_for_load_state("domcontentloaded")
                    page.locator(".col-12").first.click()
                    page.wait_for_load_state("domcontentloaded")
                    page.get_by_role("textbox", name="아이디").click()
                    page.get_by_role("textbox", name="아이디").fill("admin48")
                    page.get_by_role("textbox", name="아이디").press("Tab")
                    page.get_by_role("textbox", name="비밀번호").fill("tkfkd")
                    page.get_by_role("button", name=" 로그인").click()
                    page.wait_for_load_state("domcontentloaded")

                    self.log_message(self.popup_log, "관리자 페이지 이동 중...")
                    page.get_by_role("link", name="관리자").click()
                    page.wait_for_load_state("domcontentloaded")
                    page.locator("a").filter(has_text="웹사이트 관리").click()
                    page.wait_for_load_state("domcontentloaded")
                    page.get_by_role("link", name="팝업창").click()
                    page.wait_for_load_state("domcontentloaded")

                    self.log_message(self.popup_log, "팝업창 수정 중...")
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

                    self.log_message(self.popup_log, "완료! 브라우저 종료 중...")
                    context.close()
                    browser.close()

                    self.log_message(self.popup_log, "✓ 팝업창 수정이 완료되었습니다.")
                    messagebox.showinfo("완료", "팝업창 수정이 완료되었습니다.")

            except Exception as e:
                self.log_message(self.popup_log, f"✗ 오류 발생: {str(e)}")
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


