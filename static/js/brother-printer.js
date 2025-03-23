// Script para impresión con impresora Brother TD-40 usando bpac-js
document.addEventListener('DOMContentLoaded', function() {
    // Verificar si hay un botón de impresión Brother en la página
    const brotherPrintBtn = document.getElementById("brother-print-btn");
    if (!brotherPrintBtn) return;

    // Cargar la biblioteca bpac-js
    const scriptTag = document.createElement('script');
    scriptTag.src = "https://cdn.jsdelivr.net/npm/bpac-js@latest/dist/index.js";
    scriptTag.onload = initBrotherPrinting;
    document.head.appendChild(scriptTag);

    function initBrotherPrinting() {
        console.log("Biblioteca de Brother cargada correctamente");
        
        brotherPrintBtn.addEventListener("click", async function(e) {
            e.preventDefault();
            
            try {
                // Obtener datos del formulario o elementos de la página
                const productName = document.getElementById("product-name").textContent || "";
                const conservationType = document.getElementById("conservation-type").textContent || "";
                const preparedBy = document.getElementById("prepared-by").textContent || "";
                const startDate = document.getElementById("start-date").textContent || "";
                const expiryDate = document.getElementById("expiry-date").textContent || "";
                const secondaryExpiryDate = document.getElementById("secondary-expiry-date") ? 
                    document.getElementById("secondary-expiry-date").textContent : "";

                // Crear instancia de BrotherSdk
                const BrotherSdk = window.BrotherSdk;
                if (!BrotherSdk) {
                    console.error("No se pudo cargar la biblioteca BrotherSdk");
                    showPrintMessage("Error: No se pudo cargar la biblioteca de impresión", true);
                    return;
                }

                const tag = new BrotherSdk({
                    templatePath: "C:/Templates/etiqueta-producto.lbx", // Ajustar la ruta a tu plantilla
                    exportPath: "C:/Temp/", // Carpeta temporal para exportar
                });

                // Los datos deben coincidir con los objetos/variables en la plantilla
                const data = {
                    producto: productName,
                    conservacion: conservationType,
                    preparado: preparedBy,
                    fecha: startDate,
                    caducidad: expiryDate,
                    caducidadPrimaria: secondaryExpiryDate
                };

                const options = {
                    copies: parseInt(document.getElementById("quantity").value || "1"), 
                    printName: "Etiqueta-Producto", 
                    highResolution: true
                };

                showPrintMessage("Enviando a la impresora Brother...");
                
                const isPrinted = await tag.print(data, options);
                
                if (isPrinted) {
                    showPrintMessage("Etiqueta enviada correctamente a la impresora Brother");
                } else {
                    showPrintMessage("No se pudo imprimir en la impresora Brother", true);
                }
            } catch (error) {
                console.error("Error al imprimir con Brother:", error);
                showPrintMessage("Error al imprimir: " + (error.message || "Error desconocido"), true);
            }
        });
    }

    function showPrintMessage(message, isError = false) {
        const messageArea = document.getElementById("print-message") || createMessageArea();
        messageArea.textContent = message;
        messageArea.className = isError ? "alert alert-danger mt-3" : "alert alert-success mt-3";
        messageArea.style.display = "block";
        
        // Ocultar el mensaje después de 5 segundos
        setTimeout(() => {
            messageArea.style.display = "none";
        }, 5000);
    }

    function createMessageArea() {
        const messageArea = document.createElement("div");
        messageArea.id = "print-message";
        messageArea.className = "alert alert-info mt-3";
        messageArea.style.display = "none";
        
        // Insertar después del botón de impresión
        brotherPrintBtn.parentNode.insertBefore(messageArea, brotherPrintBtn.nextSibling);
        
        return messageArea;
    }
});