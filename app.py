import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="امتیاز واشنگتن",
    page_icon="🃏",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- Custom CSS ----------
st.markdown("""
<style>
    .stApp {
        max-width: 700px;
        margin: auto;
    }
    h1 {
        text-align: center;
        color: #1F4E79;
        font-size: 1.7rem !important;
        margin-bottom: 0.2rem;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        background-color: #f0f7ff;
        border: 1px solid #d0e3f7;
        border-radius: 10px;
        padding: 8px 12px;
    }
    .score-ok {
        color: #006100;
        font-weight: bold;
        font-size: 1.15rem;
    }
    .score-zero {
        color: #9C0006;
        font-weight: bold;
        font-size: 1.15rem;
    }
    .stAlert {
        direction: rtl;
        text-align: right;
    }
    /* Force RTL for the guide expander content */
    div[data-testid="stExpander"] div[data-testid="stMarkdownContainer"] {
        direction: rtl;
        text-align: right;
    }
    input[type=number] {
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🃏 امتیازدهی بازی واشنگتن")
st.caption("ساده • کاربردی • مخصوص موبایل")

# ---------- Guide ----------
with st.expander("📖 راهنمای استفاده (حتماً بخوانید)", expanded=True):
    st.markdown("""
<div dir="rtl" style="text-align: right; line-height: 1.8;">

<strong>نحوه کار:</strong>

۱. تعداد بازیکن و اسم‌ها را تنظیم کنید.<br>
۲. در <strong>ابتدای هر دور</strong>، برای هر بازیکن مقدار <strong>Bid (پیشنهاد)</strong> را وارد کنید.<br>
۳. بعد از تمام شدن دور، مقدار <strong>Taken (گرفته‌شده)</strong> را برای هر بازیکن وارد کنید.<br>
۴. امتیاز به صورت خودکار محاسبه می‌شود:<br>
&nbsp;&nbsp;&nbsp;• اگر Bid = Taken باشد → امتیاز = ۱۰ + Bid<br>
&nbsp;&nbsp;&nbsp;• در غیر این صورت → ۰<br>
۵. دو چک مهم در هر دور نمایش داده می‌شود:<br>
&nbsp;&nbsp;&nbsp;• جمع Bidها نباید مساوی تعداد کارت آن دور باشد<br>
&nbsp;&nbsp;&nbsp;• حداقل یک نفر باید امتیاز صفر گرفته باشد

</div>
    """, unsafe_allow_html=True)

# ---------- Session State ----------
if "players" not in st.session_state:
    st.session_state.players = ["بازیکن ۱", "بازیکن ۲", "بازیکن ۳", "بازیکن ۴", "بازیکن ۵"]
if "num_players" not in st.session_state:
    st.session_state.num_players = 5
if "rounds_data" not in st.session_state:
    st.session_state.rounds_data = {}

# ---------- Settings ----------
with st.expander("⚙️ تنظیمات بازی", expanded=False):
    num = st.radio(
        "تعداد بازیکن",
        options=[5, 6],
        format_func=lambda x: "۵ نفره" if x == 5 else "۶ نفره",
        index=0 if st.session_state.num_players == 5 else 1,
        horizontal=True
    )
    if num != st.session_state.num_players:
        st.session_state.num_players = num
        if num == 5:
            st.session_state.players = st.session_state.players[:5]
        else:
            while len(st.session_state.players) < 6:
                st.session_state.players.append(f"بازیکن {len(st.session_state.players)+1}")
        st.rerun()

    st.write("اسم بازیکن‌ها:")
    new_names = []
    # Sequential order (1,2,3,4...) instead of odd/even columns
    for i in range(st.session_state.num_players):
        name = st.text_input(
            f"بازیکن {i+1}",
            value=st.session_state.players[i],
            key=f"name_{i}"
        )
        new_names.append(name.strip() or f"بازیکن {i+1}")
    st.session_state.players = new_names

# Determine rounds
if st.session_state.num_players == 5:
    card_counts = list(range(10, 0, -1))
else:
    card_counts = list(range(9, 0, -1))

st.divider()

# ---------- Input Rounds ----------
st.subheader("ثبت امتیاز دورها")

tab_labels = [f"{c} کارت" for c in card_counts]
tabs = st.tabs(tab_labels)

total_scores = {p: 0 for p in st.session_state.players}

for idx, cards in enumerate(card_counts):
    with tabs[idx]:
        st.markdown(f"**دور با {cards} کارت**")

        if cards not in st.session_state.rounds_data:
            st.session_state.rounds_data[cards] = {
                p: {"call": None, "taken": None} for p in st.session_state.players
            }

        for p in st.session_state.players:
            if p not in st.session_state.rounds_data[cards]:
                st.session_state.rounds_data[cards][p] = {"call": None, "taken": None}

        calls = []
        takens = []
        scores = []

        for i, p in enumerate(st.session_state.players):
            st.markdown(f"**{p}**")
            c1, c2, c3 = st.columns([1, 1, 1])

            with c1:
                current_call = st.session_state.rounds_data[cards][p]["call"]
                new_call = st.number_input(
                    "Bid (پیشنهاد)",
                    min_value=0,
                    max_value=cards,
                    value=current_call if current_call is not None else None,
                    key=f"call_{cards}_{p}",
                    placeholder="—"
                )
                st.session_state.rounds_data[cards][p]["call"] = new_call
                calls.append(new_call)

            with c2:
                current_taken = st.session_state.rounds_data[cards][p]["taken"]
                new_taken = st.number_input(
                    "Taken (گرفته‌شده)",
                    min_value=0,
                    max_value=cards,
                    value=current_taken if current_taken is not None else None,
                    key=f"taken_{cards}_{p}",
                    placeholder="—"
                )
                st.session_state.rounds_data[cards][p]["taken"] = new_taken
                takens.append(new_taken)

            with c3:
                if new_call is not None and new_taken is not None:
                    score = 10 + new_call if new_call == new_taken else 0
                else:
                    score = None
                scores.append(score)

                if score is None:
                    st.markdown("<div style='padding-top:1.7rem; color:#999; text-align:center'>—</div>", unsafe_allow_html=True)
                else:
                    color = "score-ok" if score > 0 else "score-zero"
                    st.markdown(
                        f"<div class='{color}' style='padding-top:1.7rem; text-align:center'>{score}</div>",
                        unsafe_allow_html=True
                    )

            if score is not None:
                total_scores[p] += score

            st.markdown("---")

        # Checks
        valid_calls = [c for c in calls if c is not None]
        valid_scores = [s for s in scores if s is not None]

        if len(valid_calls) > 0:
            sum_calls = sum(valid_calls)

            if sum_calls == cards:
                st.error(f"❌ جمع Bidها ({sum_calls}) نباید مساوی {cards} باشد")
            else:
                st.success(f"✓ جمع Bidها = {sum_calls} (درست)")

            if len(valid_scores) == 0:
                st.info("هنوز امتیازی ثبت نشده")
            elif 0 in valid_scores:
                st.success("✓ حداقل یک صفر وجود دارد")
            else:
                st.error("❌ هیچ صفری وجود ندارد (احتمالاً اشتباه)")
        else:
            st.info("Bid و Taken را وارد کنید")

st.divider()

# ---------- Final Ranking ----------
st.subheader("🏆 رتبه‌بندی نهایی")

ranking = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)

rank_cols = st.columns(min(3, st.session_state.num_players))
medals = ["🥇", "🥈", "🥉"] + ["▫️"] * 3

for i, (player, score) in enumerate(ranking):
    col_idx = i % 3
    with rank_cols[col_idx]:
        medal = medals[i] if i < len(medals) else "▫️"
        st.metric(label=f"{medal} {player}", value=f"{score} امتیاز")

st.markdown("### جدول کامل")
df_data = [{"رتبه": i+1, "بازیکن": player, "امتیاز نهایی": score} for i, (player, score) in enumerate(ranking)]
df = pd.DataFrame(df_data)
st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
if st.button("🔄 شروع بازی جدید", type="primary", use_container_width=True):
    st.session_state.rounds_data = {}
    st.rerun()

st.caption("ساخته شده برای بازی واشنگتن")
