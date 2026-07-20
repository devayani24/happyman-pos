export function formatTime(timeString) {
    // timeString is like "20:15:30" (24-hour)
    // Want: "8:15 PM"
    
    if (!timeString) return '';
    
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours, 10);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;  // 0 becomes 12, 13 becomes 1
    
    return `${displayHour}:${minutes} ${ampm}`;
}