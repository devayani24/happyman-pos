function currentDateTime() {
  const formattedDate = new Date().toLocaleString('en-GB', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  });

  document.querySelector('.js-date-time').textContent = formattedDate;
}

export function startClock() {
  currentDateTime();                                  // show immediately

  // Wait until the next full minute, then update every 60 seconds
  const msToNextMinute = 60000 - (Date.now() % 60000);
  setTimeout(() => {
    currentDateTime();
    setInterval(currentDateTime, 60000);
  }, msToNextMinute);
}
