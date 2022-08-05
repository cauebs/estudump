from textwrap import dedent

import streamlit as st

from cagr import CAGR

st.title("Listar números de matrícula de estudantes da UFSC")

username = st.text_input("idUFSC")
password = st.text_input(
    "Senha",
    type="password",
    help=(
        "Pode confiar: o código fonte pode ser verificado "
        "abrindo o menu lá em cima e clicando em 'View app source'"
    ),
)
prefix = st.text_input("Filtrar números de matrículas com esse prefixo")
start = st.button("Listar", disabled=(not username or not password))

if not start:
    st.stop()

with st.spinner("Autenticando no fórum do CAGR"):
    try:
        cagr = CAGR.login(username, password)
    except CAGR.AuthError:
        st.error("Erro de autenticação.")
        st.stop()

with st.spinner("Listando cursos"):
    rooms = cagr.list_rooms()

progress_label = st.empty()
progress_bar = st.progress(0)
student_ids = []
for i, room in enumerate(rooms):
    progress_label.write(f"Listando estudantes de {room.name}...")
    student_ids.extend(cagr.list_student_ids(room.id))
    progress_bar.progress(i / len(rooms))

contents = "\n".join(id for id in student_ids if id.startswith(prefix))
st.success("Pronto!")
st.download_button("Baixar lista", contents, file_name=f"matriculas{prefix}.csv")

with st.expander("O que eu faço com isso?"):
    left, right = st.columns(2)
    with left:
        st.image("menu.png")
    with right:
        st.write(dedent(
            "- No menu Administração do Moodle (1);\n"
            "- Expanda o item Usuários (2);\n"
            "- Entre em Inscrições em Massa (3)."
        ))

    st.write(dedent(
        "- Selecione Matrícula como Tipo de Identificador (1);\n"
        "- Cole os números de matrícula no campo de texto Identificadores (2);\n"
        "- Selecione Estudante como Papel (3);\n"
        "- Pressione o botão Inscrição em massa (4)."
    ))
    st.image("form.png")

    st.warning(
        "Atenção: "
        "o Moodle pode engasgar se tentar engolir muitos números de matrícula de uma só vez. "
        "5mil por vez é um número que sabemos que funciona. Fatia o arquivo se necessário."
    )
