const char MAIN_page[] PROGMEM = R"=====(

<script language = "JavaScript">
    function guardarInfo(form){
         
        var pass = form.pass.value;
        var nombre = form.nombre.value;
         
        var jsonFormInfo = JSON.stringify({
            pass:pass, 
            nombre: nombre
        });
 
        window.alert("Informacion guardada:" + jsonFormInfo);
         
    }
</script>
 
<h1>Bienvenido</h1>
<form onSubmit = "event.preventDefault(); guardarInfo(this);">
    <label class="label">Network Name</label>
    <input type = "text" name = "nombre"/>
    <br/>
    <label>Password</label>
    <input type = "text" name = "pass"/>
    <br/>
    <input type="submit" value="Submit">
</form>

)=====";