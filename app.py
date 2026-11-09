import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="امتیاز واشنگتن",
    page_icon="🃏",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- Custom CSS for clean mobile look ----------
st.markdown("""
<style>
    .stApp {
        max-width: 900px;
        margin: auto;
    }
    h1 {
        text-align: center;
        color: #1F4E79;
        font-size: 1.8rem !important;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        background-color: #f0f7ff;
        border: 1px solid #d0e3f7;
        border-radius: 10px;
        padding: 10px;
    }
    .score-ok {
        color: #006100;
        font-weight: bold;
    }
    .score-zero {
        color: #9C0006;
        font-weight: bold;
    }
    /* Better RTL support for messages */
    .stAlert {
        direction: rtl;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

st.title("🃏 امتیازدهی بازی واشنگتن")
st.caption("ساده • کاربردی • مخصوص موبایل")

# ---------- Session State ----------
if "players" not in st.session_state:
    st.session_state.players = ["بازیکن ۱", "بازیکن ۲", "بازیکن ۳", "بازیکن ۴", "بازیکن ۵"]
if "num_players" not in st.session_state:
    st.session_state.num_players = 5
if "rounds_data" not in st.session_state:
    st.session_state.rounds_data = {}  # {cards: {player: {"call": None, "taken": None}}}

# ---------- Settings ----------
with st.expander("⚙️ تنظیمات بازی", expanded=True):
    col1, col2 = st.columns([1, 2])
    
    with col1:
        num = st.radio("تعداد بازیکن", [5, 6], index=0 if st.session_state.num_players == 5 else 1, horizontal=True)
        if num != st.session_state.num_players:
            st.session_state.num_players = num
            if num == 5:
                st.session_state.players = st.session_state.players[:5]
            else:
                while len(st.session_state.players) < 6:
                    st.session_state.players.append(f"بازیکن {len(st.session_state.players)+1}")
            st.rerun()
    
    with col2:
        st.write("اسم بازیکن‌ها:")
        new_names = []
        name_cols = st.columns(st.session_state.num_players)
        for i in range(st.session_state.num_players):
            with name_cols[i]:
                name = st.text_input(
                    f"P{i+1}",
                    value=st.session_state.players[i],
                    key=f"name_{i}",
                    label_visibility="collapsed"
                )
                new_names.append(name.strip() or f"بازیکن {i+1}")
        st.session_state.players = new_names

# Determine rounds
if st.session_state.num_players == 5:
    card_counts = list(range(10, 0, -1))  # 10 → 1
else:
    card_counts = list(range(9, 0, -1))   # 9 → 1

st.divider()

# ---------- Input Rounds ----------
st.subheader("ثبت امتیاز دورها")

tab_labels = [f"{c} کارت" for c in card_counts]
tabs = st.tabs(tab_labels)

total_scores = {p: 0 for p in st.session_state.players}

for idx, cards in enumerate(card_counts):
    with tabs[idx]:
        st.markdown(f"**دور با {cards} کارت**")
        
        # Initialize data for this round if needed
        if cards not in st.session_state.rounds_data:
            st.session_state.rounds_data[cards] = {
                p: {"call": None, "taken": None} for p in st.session_state.players
            }
        
        # Ensure all current players exist in data
        for p in st.session_state.players:
            if p not in st.session_state.rounds_data[cards]:
                st.session_state.rounds_data[cards][p] = {"call": None, "taken": None}
        
        # Header
        header_cols = st.columns([2] + [1]*st.session_state.num_players)
        header_cols[0].markdown("**بازیکن**")
        for i, p in enumerate(st.session_state.players):
            header_cols[i+1].markdown(f"**{p}**")
        
        # Call row - default empty (None)
        call_cols = st.columns([2] + [1]*st.session_state.num_players)
        call_cols[0].markdown("Call")
        calls = []
        for i, p in enumerate(st.session_state.players):
            current = st.session_state.rounds_data[cards][p]["call"]
            # Use None as default so the field starts empty
            new_val = call_cols[i+1].number_input(
                f"call_{cards}_{i}",
                min_value=0,
                max_value=cards,
                value=current if current is not None else None,
                key=f"call_{cards}_{p}",
                label_visibility="collapsed",
                placeholder="—"
            )
            st.session_state.rounds_data[cards][p]["call"] = new_val
            calls.append(new_val)
        
        # Taken row - default empty
        taken_cols = st.columns([2] + [1]*st.session_state.num_players)
        taken_cols[0].markdown("Taken")
        takens = []
        for i, p in enumerate(st.session_state.players):
            current = st.session_state.rounds_data[cards][p]["taken"]
            new_val = taken_cols[i+1].number_input(
                f"taken_{cards}_{i}",
                min_value=0,
                max_value=cards,
                value=current if current is not None else None,
                key=f"taken_{cards}_{p}",
                label_visibility="collapsed",
                placeholder="—"
            )
            st.session_state.rounds_data[cards][p]["taken"] = new_val
            takens.append(new_val)
        
        # Calculate scores only when both Call and Taken are filled
        scores = []
        filled_count = 0
        for call, taken in zip(calls, takens):
            if call is not None and taken is not None:
                filled_count += 1
                if call == taken:
                    score = 10 + call
                else:
                    score = 0
            else:
                score = None
            scores.append(score)
        
        # Update total only with valid scores
        for p, score in zip(st.session_state.players, scores):
            if score is not None:
                total_scores[p] += score
        
        # Show scores
        score_cols = st.columns([2] + [1]*st.session_state.num_players)
        score_cols[0].markdown("**امتیاز**")
        for i, score in enumerate(scores):
            if score is None:
                score_cols[i+1].markdown("<div style='text-align:center; color:#999'>—</div>", unsafe_allow_html=True)
            else:
                color = "score-ok" if score > 0 else "score-zero"
                score_cols[i+1].markdown(
                    f"<div class='{color}' style='text-align:center; font-size:1.2rem'>{score}</div>",
                    unsafe_allow_html=True
                )
        
        # Checks - only when at least one player has both values filled
        valid_calls = [c for c in calls if c is not None]
        valid_scores = [s for s in scores if s is not None]
        
        if len(valid_calls) > 0:
            sum_calls = sum(valid_calls)
            
            check_cols = st.columns(2)
            
            with check_cols[0]:
                if sum_calls == cards:
                    st.error(f"❌ جمع Callها ({sum_calls}) نباید مساوی {cards} باشد")
                else:
                    st.success(f"✓ جمع Callها = {sum_calls} (درست)")
            
            with check_cols[1]:
                if len(valid_scores) == 0:
                    st.info("هنوز امتیازی ثبت نشده")
                elif 0 in valid_scores:
                    st.success("✓ حداقل یک صفر وجود دارد")
                else:
                    st.error("❌ هیچ صفری وجود ندارد (احتمالاً اشتباه)")
        else:
            st.info("Call و Taken را وارد کنید")

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
df_data = []
for i, (player, score) in enumerate(ranking):
    df_data.append({
        "رتبه": i + 1,
        "بازیکن": player,
        "امتیاز نهایی": score
    })
df = pd.DataFrame(df_data)
st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
if st.button("🔄 شروع بازی جدید", type="primary", use_container_width=True):
    st.session_state.rounds_data = {}
    st.rerun()

st.caption("ساخته شده برای بازی واشنگتن • نسخه ساده و کاربردی")
