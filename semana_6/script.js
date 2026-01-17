document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registroForm');
    const inputs = document.querySelectorAll('input');
    const btnSubmit = document.getElementById('btnSubmit');
    const btnReset = document.getElementById('btnReset');

    // EXPRESIÓN REGULAR CORREGIDA:
    // (?=.*\d) -> Busca al menos un dígito
    // (?=.*[\W_]) -> Busca al menos un carácter que NO sea letra/número (simbolo) o un guion bajo
    // .{8,} -> Cualquier carácter, mínimo 8 veces
    const patterns = {
        password: /^(?=.*\d)(?=.*[\W_]).{8,}$/, 
        email: /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/
    };

    const fields = {
        nombre: false,
        email: false,
        password: false,
        confirmPassword: false,
        edad: false
    };

    const validateInput = (e) => {
        const input = e.target;
        const value = input.value.trim();
        
        switch (input.name) {
            case 'nombre':
                validateField(input, value.length >= 3);
                break;
            case 'email':
                validateField(input, patterns.email.test(value));
                break;
            case 'password':
                validateField(input, patterns.password.test(value));
                validateConfirmPassword(); 
                break;
            case 'confirmPassword':
                validateConfirmPassword();
                break;
            case 'edad':
                validateField(input, value !== '' && parseInt(value) >= 18);
                break;
        }
        checkFormValidity();
    };

    const validateField = (input, condition) => {
        if (condition) {
            input.classList.remove('invalido');
            input.classList.add('valido');
            fields[input.name] = true;
        } else {
            input.classList.remove('valido');
            input.classList.add('invalido');
            fields[input.name] = false;
        }
    };

    const validateConfirmPassword = () => {
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('confirmPassword');
        
        // Solo es válido si no está vacío y coincide con el original
        const condition = confirmPassword.value.trim() !== '' && 
                          confirmPassword.value === password.value;
        
        validateField(confirmPassword, condition);
    };

    const checkFormValidity = () => {
        const allValid = Object.values(fields).every(value => value === true);
        
        // ESTO ES PARA DEPURAR:
        // Abre la consola (F12) y verás qué campo sigue siendo "false"
        console.log("Estado del formulario:", fields); 
        console.log("¿Habilitar botón?:", allValid);

        btnSubmit.disabled = !allValid;
    };

    inputs.forEach(input => {
        input.addEventListener('input', validateInput);
        input.addEventListener('blur', validateInput);
    });

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        if (!btnSubmit.disabled) {
            alert('¡Formulario enviado con éxito!');
            form.reset();
            resetStyles();
        }
    });

    btnReset.addEventListener('click', () => {
        form.reset();
        resetStyles();
    });

    const resetStyles = () => {
        inputs.forEach(input => {
            input.classList.remove('valido', 'invalido');
        });
        btnSubmit.disabled = true;
        Object.keys(fields).forEach(key => fields[key] = false);
    };
});