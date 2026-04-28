import os
import json
import datetime
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image

# 테마 설정
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# 시뮬레이션용 영화 데이터베이스 (검색 시 활용)
MOCK_MOVIE_DB = [
    {"title": "인셉션", "date": "2010-07-21", "director": "크리스토퍼 놀란", "genre": "SF/액션"},
    {"title": "인터스텔라", "date": "2014-11-06", "director": "크리스토퍼 놀란", "genre": "SF/드라마"},
    {"title": "기생충", "date": "2019-05-30", "director": "봉준호", "genre": "드라마/스릴러"},
    {"title": "어벤져스: 엔드게임", "date": "2019-04-24", "director": "안소니 루소", "genre": "액션/SF"},
    {"title": "너의 이름은.", "date": "2017-01-04", "director": "신카이 마코토", "genre": "애니메이션"},
    {"title": "라라랜드", "date": "2016-12-07", "director": "데미언 셔젤", "genre": "로맨스/뮤지컬"},
    {"title": "타이타닉", "date": "1998-02-20", "director": "제임스 카메론", "genre": "로맨스/드라마"},
    {"title": "다크 나이트", "date": "2008-08-06", "director": "크리스토퍼 놀란", "genre": "액션/스릴러"},
    {"title": "조커", "date": "2019-10-02", "director": "토드 필립스", "genre": "드라마/범죄"},
    {"title": "엘리멘탈", "date": "2023-06-14", "director": "피터 손", "genre": "애니메이션"},
]

class MovieLogApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CineLog: 나만의 영화 아카이브")
        self.geometry("1000x700")
        
        self.db_file = "my_movies.json"
        self.reviews = self.load_data()

        # UI 레이아웃 구성
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 사이드바 (기록하기 패널)
        self.sidebar = ctk.CTkFrame(self, width=350, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.init_sidebar()

        # 메인 영역 (목록 보기)
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.init_main_view()

    def load_data(self):
        if os.path.exists(self.db_file):
            with open(self.db_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_data(self):
        with open(self.db_file, "w", encoding="utf-8") as f:
            json.dump(self.reviews, f, ensure_ascii=False, indent=4)

    def init_sidebar(self):
        lbl_title = ctk.CTkLabel(self.sidebar, text="🎬 새 영화 기록", font=("Arial", 24, "bold"))
        lbl_title.pack(pady=(30, 20), padx=20)

        # 검색 영역
        search_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        search_frame.pack(fill="x", padx=20)
        
        self.entry_search = ctk.CTkEntry(search_frame, placeholder_text="영화 제목 검색...")
        self.entry_search.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_search = ctk.CTkButton(search_frame, text="🔍", width=40, command=self.search_movie)
        btn_search.pack(side="right")

        # 정보 입력 필드
        self.info_labels = {}
        fields = [("제목", "title"), ("개봉일", "date"), ("감독", "director"), ("장르", "genre")]
        
        self.entry_vars = {}
        for label, key in fields:
            lbl = ctk.CTkLabel(self.sidebar, text=label, font=("Arial", 13))
            lbl.pack(anchor="w", padx=25, pady=(10, 0))
            
            var = ctk.StringVar()
            entry = ctk.CTkEntry(self.sidebar, textvariable=var, width=300)
            entry.pack(padx=20, pady=(0, 5))
            self.entry_vars[key] = var

        lbl_rating = ctk.CTkLabel(self.sidebar, text="내 평점 (1-5)", font=("Arial", 13))
        lbl_rating.pack(anchor="w", padx=25, pady=(10, 0))
        self.slider_rating = ctk.CTkSlider(self.sidebar, from_=1, to=5, number_of_steps=4)
        self.slider_rating.pack(padx=20, pady=5)
        self.slider_rating.set(5)

        lbl_review = ctk.CTkLabel(self.sidebar, text="한 줄 평", font=("Arial", 13))
        lbl_review.pack(anchor="w", padx=25, pady=(10, 0))
        self.textbox_review = ctk.CTkTextbox(self.sidebar, height=100)
        self.textbox_review.pack(padx=20, pady=5, fill="x")

        btn_save = ctk.CTkButton(self.sidebar, text="기록 저장하기", height=45, fg_color="#2FA572", hover_color="#106A43", command=self.add_review)
        btn_save.pack(padx=20, pady=20, fill="x")

    def init_main_view(self):
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        lbl_main = ctk.CTkLabel(header_frame, text="My Movie Archive", font=("Arial", 28, "bold"))
        lbl_main.pack(side="left")

        btn_refresh = ctk.CTkButton(header_frame, text="새로고침", width=100, command=self.render_cards)
        btn_refresh.pack(side="right")

        # 스크롤 가능한 카드 영역
        self.scroll_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)
        
        self.render_cards()

    def search_movie(self):
        query = self.entry_search.get().strip()
        if not query: return
        
        found = False
        for movie in MOCK_MOVIE_DB:
            if query in movie["title"]:
                for key in ["title", "date", "director", "genre"]:
                    self.entry_vars[key].set(movie[key])
                found = True
                break
        
        if not found:
            messagebox.showinfo("검색 결과", "데이터베이스에 해당 영화가 없습니다. 직접 입력해주세요.")

    def add_review(self):
        data = {
            "title": self.entry_vars["title"].get(),
            "date": self.entry_vars["date"].get(),
            "director": self.entry_vars["director"].get(),
            "genre": self.entry_vars["genre"].get(),
            "rating": int(self.slider_rating.get()),
            "review": self.textbox_review.get("1.0", "end-1c"),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        if not data["title"]:
            messagebox.showwarning("경고", "영화 제목은 필수입니다.")
            return

        self.reviews.insert(0, data)
        self.save_data()
        self.render_cards()
        
        # 입력창 초기화
        for var in self.entry_vars.values(): var.set("")
        self.textbox_review.delete("1.0", "end")
        messagebox.showinfo("성공", "영화 기록이 저장되었습니다.")

    def render_cards(self):
        # 기존 카드 제거
        for child in self.scroll_frame.winfo_children():
            child.destroy()

        if not self.reviews:
            lbl_empty = ctk.CTkLabel(self.scroll_frame, text="아직 기록된 영화가 없습니다.\n왼쪽 패널에서 첫 영화를 기록해보세요!", font=("Arial", 16), pady=100)
            lbl_empty.pack()
            return

        for i, rev in enumerate(self.reviews):
            card = ctk.CTkFrame(self.scroll_frame, corner_radius=10, height=150)
            card.pack(fill="x", padx=10, pady=10)
            
            # 레이아웃 내부 구성
            inner_frame = ctk.CTkFrame(card, fg_color="transparent")
            inner_frame.pack(fill="both", expand=True, padx=15, pady=10)
            
            # 왼쪽: 제목 및 정보
            info_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True)
            
            lbl_title = ctk.CTkLabel(info_frame, text=rev["title"], font=("Arial", 18, "bold"), anchor="w")
            lbl_title.pack(fill="x")
            
            lbl_meta = ctk.CTkLabel(info_frame, text=f"{rev['date']} | {rev['director']} | {rev['genre']}", font=("Arial", 12), text_color="gray", anchor="w")
            lbl_meta.pack(fill="x")
            
            lbl_stars = ctk.CTkLabel(info_frame, text="★" * rev["rating"] + "☆" * (5-rev["rating"]), font=("Arial", 16), text_color="#FFD700", anchor="w")
            lbl_stars.pack(fill="x", pady=5)
            
            lbl_text = ctk.CTkLabel(info_frame, text=rev["review"], font=("Arial", 14), anchor="w", wraplength=400, justify="left")
            lbl_text.pack(fill="x")

            # 오른쪽: 삭제 버튼
            btn_delete = ctk.CTkButton(inner_frame, text="삭제", width=60, fg_color="#CC3333", hover_color="#991111", command=lambda idx=i: self.delete_review(idx))
            btn_delete.pack(side="right", padx=10)

    def delete_review(self, index):
        if messagebox.askyesno("삭제", "이 기록을 삭제하시겠습니까?"):
            self.reviews.pop(index)
            self.save_data()
            self.render_cards()

if __name__ == "__main__":
    app = MovieLogApp()
    app.mainloop()
