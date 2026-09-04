#!/usr/bin/env python3
import math
import numpy as np
import streamlit as st
import plotly.graph_objects as go

# 1. Настройка на страницата
st.set_page_config(page_title="Инженерен Калкулатор Вита Стълба", layout="wide")

st.title("🏗️ Професионален Калкулатор за Вита Стълба")
st.write("С помощни указания за оптимални инженерни граници.")

# 2. Страничен панел (Входни данни с помощни описания)
with st.sidebar:
    st.header("🎛️ Параметри")
    H_in = st.number_input("Обща височина H (мм)", value=2700.0, step=10.0,
                           help="Стандартна височина от готов под до готов под.")
    
    N_in = st.number_input("Брой стъпала N", min_value=1, value=13, step=1,
                           help="Регулирайте, за да постигнете височина на стъпката между 170 и 210 мм.")
    
    T_in = st.number_input("Дебелина на стъпалото T (мм)", value=60.0, step=1.0,
                           help="Обикновено между 40 и 60 мм в зависимост от материала.")
    
    D_pipe = st.number_input("Диаметър на тръбата D (мм)", value=133.0, step=1.0,
                             help="Оптимално: 102 - 159 мм за конструктивна здравина.")
    
    L_in = st.number_input("Дължина на бедрото L (мм)", value=971.0, step=1.0,
                           help="Дължината на самото стъпало (без радиуса на тръбата).")
    
    W_out_in = st.number_input("Външна ширина на детайла W_out (мм)", value=470.0, step=10.0,
                               help="Ширина на заготовката в широкия край.")
    
    total_rot = st.number_input("Общо завъртане (градуси)", value=250.0, step=10.0,
                                help="Зависи от отвора в плочата. Стандартно: 240° - 360°.")
    
    posoka = st.radio("Посока нагоре:", ("Надясно (По часовника)", "Наляво (Обратно)"))
    is_clockwise = True if "Надясно" in posoka else False

# 3. МАТЕМАТИЧЕСКИ ИЗЧИСЛЕНИЯ
h_step = H_in / N_in
H_clear = h_step - T_in
R_in = D_pipe / 2
R_out = math.sqrt(L_in**2 + R_in**2)
beta_rad = math.radians(total_rot / N_in)

W_in_fixed = D_pipe
W_at_2_3_physical = W_in_fixed + (2/3) * (W_out_in - W_in_fixed)
R_2_3 = R_in + (2/3) * L_in
W_effective_2_3 = R_2_3 * beta_rad
overlap_2_3 = W_at_2_3_physical - W_effective_2_3

# Изчисление на застъпването в най-външната точка (по външния ръб)
W_effective_out = R_out * beta_rad
overlap_out = W_out_in - W_effective_out

alpha_deg = math.degrees(math.atan2(W_out_in/2 - W_in_fixed/2, L_in)) * 2

total_arc_length = R_out * math.radians(total_rot)
stair_slope_deg = math.degrees(math.atan(H_in / total_arc_length))

# 4. ПОКАЗВАНЕ НА РЕЗУЛТАТИТЕ
col_res, col_viz = st.columns([1, 2])

with col_res:
    st.subheader("📊 Анализ и Норми")
    
    # Височина на стъпката с подсказка
    st.metric("Височина на стъпката", f"{h_step:.1f} мм", 
              help="Оптимално: 170-190 мм. \nДопустимо за вита стълба: до 220 мм.")
    
    # Ефективна ширина с подсказка
    st.metric("Ефективна стъпница (2/3 L)", f"{W_effective_2_3:.1f} мм",
              help="Това е мястото за стъпване. \nОптимално: 220-280 мм. \nМинимум: 200 мм за безопасно слизане.")

    # Наклон с подсказка
    st.metric("Наклон на стълбата", f"{stair_slope_deg:.1f}°",
              help="Оптимално: 30° - 35°. \nНад 45° стълбата става стръмна и трудна за ползване.")

    st.write("---")
    st.subheader("📐 Размери за производство")
    
    st.metric("Застъпване по външния ръб", f"{overlap_out:.1f} мм ({overlap_out/10:.1f} см)",
              help="Разстоянието, с което горното стъпало покрива долното в най-външния му ъгъл. Използва се за лесен монтаж и позициониране с ролетка.")

    st.metric("Застъпване (на 2/3)", f"{overlap_2_3:.1f} мм",
              help="Разлика между физическия детайл и свободното място по линията на ходене. \nПрепоръчително: 30-80 мм за здравина и визия.")
    
    st.metric("Физически ъгъл на рязане", f"{alpha_deg:.1f}°",
              help="Ъгълът, под който трябва да се отреже трапеца на плазма или абкант.")

    st.write("---")
    st.subheader("🧭 Допълнителни данни")
    st.write(f"Външен радиус: **{R_out:.1f} мм**")
    st.write(f"Чист просвет между стъпала: **{H_clear:.1f} мм**")
    st.info(f"Дължина за парапет: **{total_arc_length:.1f} мм**")

with col_viz:
    # --- 3D МОДЕЛ ---
    fig = go.Figure()

    # Тръба
    z_p = np.linspace(0, H_in, 50)
    theta_p = np.linspace(0, 2*np.pi, 50)
    t_grid, z_grid = np.meshgrid(theta_p, z_p)
    fig.add_trace(go.Surface(x=R_in*np.cos(t_grid), y=R_in*np.sin(t_grid), z=z_grid, 
                             colorscale='Greys', opacity=0.3, showscale=False))

    # Стъпала
    for i in range(1, N_in + 1):
        rot = math.radians((i-1) * (total_rot / N_in)) * (-1 if is_clockwise else 1)
        z1 = i * h_step
        z0 = z1 - T_in
        
        half_in, half_out = W_in_fixed / 2, W_out_in / 2
        p_loc = [(0, -half_in), (L_in, -half_out), (L_in, half_out), (0, half_in)]
        
        tx, ty = [], []
        for px, py in p_loc:
            tx.append(px * math.cos(rot) - py * math.sin(rot))
            ty.append(px * math.sin(rot) + py * math.cos(rot))
        
        c = '#1f77b4' if is_clockwise else '#ff7f0e'
        fig.add_trace(go.Mesh3d(x=tx, y=ty, z=[z1]*4, color=c, opacity=0.9))
        fig.add_trace(go.Mesh3d(x=tx, y=ty, z=[z0]*4, color=c, opacity=0.9))
        fig.add_trace(go.Scatter3d(x=tx+[tx[0]], y=ty+[ty[0]], z=[z1]*5, mode='lines', line=dict(color='black', width=2), showlegend=False))

    fig.update_layout(scene=dict(aspectmode='data'), height=800, margin=dict(l=0, r=0, b=0, t=0))
    st.plotly_chart(fig, width='stretch')
