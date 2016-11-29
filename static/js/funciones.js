function Confirmar_Password() {
  if ((document.getElementById('pwd').value) == (document.getElementById('pwd2').value)) {
    document.getElementById('form').submit();
  }
  else {
    document.getElementById('oculto').style.display = "block";
  }
}

function Mostrar_Input() {
  document.getElementById('input_materia').style.display = 'block';
}
