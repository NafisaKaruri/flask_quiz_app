document.addEventListener("DOMContentLoaded", function () {
    const text = "Welcome to the Quiz App";
    const element = document.getElementById("typewriter-text");
    const cursor = document.createElement('span');
    cursor.id = "typewriter-cursor";
    cursor.textContent = "_";
    element.appendChild(cursor);

    let index = 0;

    function typeWriter() {
        if (index < text.length) {
            element.textContent = text.substring(0, index + 1);
            element.appendChild(cursor);
            index++;
            setTimeout(typeWriter, 100); // Adjust speed by changing the timeout duration
        } //else {
            //cursor.style.display = 'none'; // Optionally hide the cursor after typing is complete
        //}
    }

    typeWriter();
});
