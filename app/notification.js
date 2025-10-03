function notification(message = '', bgcolor = 'bg-blue-500') {
    const notification = document.createElement('div');
    notification.classList.add('z-50', 'popup', 'fixed', 'top-[-100px]', 'left-0', 'w-screen', bgcolor, 'text-lg', 'font-medium', 'text-zinc-50', 'px-6', 'py-4', 'drop-shadow-3xl', 'backdrop-blur-lg', 'dm-sans', 'duration-200');

    const messageElement = document.createElement('span');
    messageElement.innerText = message;
    notification.appendChild(messageElement);
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.top = '0';
    }, 0);

    setTimeout(() => {
        notification.style.top = '-100px';
        setTimeout(() => {
        notification.remove();
        }, 300);
    }, 3000);
}
