function showCode() {
  let code = document.getElementById('code');
  let codelabel = document.getElementById('codelabel');
  if (code.style.display != 'none') {
    code.style.display = 'none';
    codelabel.style.display = 'none';
  } else {
    code.style.display = 'inline-block';
    codelabel.style.display = 'inline-block';
  }
}