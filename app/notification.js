function notification(message = '', bgcolor = 'bg-blue-500/80') {
    const overlay = document.createElement('div');
    overlay.classList.add(
        'fixed', 'inset-0', 'z-50',
        'flex', 'items-center', 'justify-center',
        'backdrop-blur-md', 'bg-black/40',
        'opacity-0', 'transition-opacity', 'duration-300'
    );

    const box = document.createElement('div');
    box.classList.add(
        'px-8', 'py-6', 'rounded-lg', 'text-center',
        'text-zinc-50', 'text-2xl', 'font-medium',
        'bg-white/00', 'shadow-2xl'
    );
    box.innerText = message;

    overlay.appendChild(box);
    document.body.appendChild(overlay);

    //fade in antimation
    requestAnimationFrame(() => {
        overlay.classList.replace('opacity-0', 'opacity-100');
    });

    //fade out after 3s animation
    setTimeout(() => {
        overlay.classList.replace('opacity-100', 'opacity-0');
        setTimeout(() => overlay.remove(), 300);
    }, 3000);
}