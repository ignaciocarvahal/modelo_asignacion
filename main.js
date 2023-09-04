document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("olugra").addEventListener("input", function() {
        document.getElementById("olugra_value").innerText = this.value;
    });
});

function processData() {
    var olugra = parseInt(document.getElementById("olugra").value);
    var startDate = document.getElementById("start_date").value;
    var startTime = document.getElementById("start_time").value;
    var endTime = document.getElementById("end_time").value;

    var combinedDateTimeStart = startDate + " " + startTime;
    var combinedDateTimeEnd = startDate + " " + endTime;

    // Resto del código para procesar los datos y actualizar la interfaz.
    // (Similar a la implementación previa con JavaScript)

    // ...
}
