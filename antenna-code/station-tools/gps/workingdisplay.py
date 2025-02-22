import curses
from serial import Serial
import time

def gps_reader(stdscr):
    # Set up curses window
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)  # Non-blocking input
    stdscr.timeout(100)  # Refresh every 100 ms
    
    # Set up colors (optional)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    
    # Initialize variables to hold the most recent GPS and waypoint data
    local_data = "Waiting for GPS data..."
    waypoint_data = "Waiting for waypoint data..."

    # Open the serial connection
    with Serial('/dev/ttyS0', 9600, timeout=3) as stream:
        while True:
            try:
                # Read raw data from the serial stream
                raw_data = stream.readline().decode('ascii', errors='ignore').strip()

                if raw_data:
                    # Check for GNGGA (GPS) data
                    if raw_data.startswith('$GNGGA'):
                        # Process GNGGA data (Local GPS)
                        parts = raw_data.split(',')
                        time_str = parts[1]
                        latitude = parts[2]
                        lat_ns = parts[3]
                        longitude = parts[4]
                        lon_ew = parts[5]
                        altitude = parts[9]

                        # Format the local data as a string with clear structure
                        local_data = (
                            f"Time:     {time_str}\n"
                            f"Latitude: {latitude} {lat_ns}\n"
                            f"Longitude:{longitude} {lon_ew}\n"
                            f"Altitude: {altitude} m"
                        )

                    # Check for GNWPL (Waypoint) data
                    elif raw_data.startswith('$GNWPL'):
                        # Process GNWPL data (Waypoint)
                        parts = raw_data.split(',')
                        waypoint = parts[1]
                        latitude = parts[2]
                        lat_ns = parts[3]
                        longitude = parts[4]
                        lon_ew = parts[5]

                        # Format the waypoint data as a string with clear structure
                        waypoint_data = (
                            f"Waypoint: {waypoint} @ {latitude} {lat_ns}, {longitude} {lon_ew}"
                        )

                    # Clear the screen and display both GPS and waypoint data
                    stdscr.clear()

                    # Header
                    stdscr.addstr(0, 2, "GPS Data Display", curses.color_pair(1))

                    # Local GPS Data at specific positions
                    stdscr.addstr(3, 2, "Local GPS Data:", curses.color_pair(1))
                    stdscr.addstr(4, 2, f"Time:     {time_str}", curses.color_pair(1))
                    stdscr.addstr(5, 2, f"Latitude: {latitude} {lat_ns}", curses.color_pair(1))
                    stdscr.addstr(6, 2, f"Longitude:{longitude} {lon_ew}", curses.color_pair(1))
                    stdscr.addstr(7, 2, f"Altitude: {altitude} m", curses.color_pair(1))

                    # Waypoint Data at specific positions
                    stdscr.addstr(10, 2, "Waypoint Data:", curses.color_pair(2))
                    stdscr.addstr(11, 2, waypoint_data, curses.color_pair(2))

                    # Refresh the screen to display changes
                    stdscr.refresh()

                    # Adjust the loop delay
                    time.sleep(0.5)

            except KeyboardInterrupt:
                break  # Allow program to exit gracefully with Ctrl+C

# Run the curses wrapper
curses.wrapper(gps_reader)
