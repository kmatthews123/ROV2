# # from serial import Serial
# # from pynmeagps import NMEAReader # type: ignore
# # import time
# # while True:
# #   with Serial('/dev/ttyS0', 9600) as stream:
# #     nmr = NMEAReader(stream)
# #     raw_data, parsed_data = nmr.read()
# #     if parsed_data is not None:
# #       print(parsed_data)
# #       time.sleep(0.5)

# import curses
# from serial import Serial
# from pynmeagps import NMEAReader # type: ignore
# import time

# def gps_reader(stdscr):
#     # Initialize curses settings
#     curses.curs_set(0)  # Hide cursor
#     stdscr.nodelay(1)   # Make getch non-blocking
#     stdscr.timeout(500) # Refresh every 500ms

#     # Define placeholder variables for GPS data
#     local_data = "Waiting for local GPS data..."
#     waypoint_data = "Waiting for waypoint data..."

#     while True:
#         # Read GPS data from serial
#         with Serial('/dev/ttyS0', 9600, timeout=1) as stream:
#             nmr = NMEAReader(stream)
#             try:
#                 raw_data, parsed_data = nmr.read()
#                 if parsed_data:
#                     # Extract GNGGA (local GPS) and GNWPL (waypoints)
#                     if parsed_data.msgID == "GNGGA":
#                         local_data = f"Lat: {parsed_data.lat} {parsed_data.NS}, Lon: {parsed_data.lon} {parsed_data.EW}, Alt: {parsed_data.alt} {parsed_data.altUnit}"
#                     elif parsed_data.msgID == "GNWPL":
#                         waypoint_data = f"Waypoint: {parsed_data.wpt}, Lat: {parsed_data.lat} {parsed_data.NS}, Lon: {parsed_data.lon} {parsed_data.EW}"
#             except Exception as e:
#                 local_data = f"Error: {str(e)}"
        
#         # Clear the screen and redraw the interface
#         stdscr.clear()
#         stdscr.addstr(1, 2, "GPS Terminal Interface", curses.A_BOLD)
#         stdscr.addstr(3, 2, f"Local GPS Data: {local_data}", curses.color_pair(1))
#         stdscr.addstr(5, 2, f"Remote Waypoint Data: {waypoint_data}", curses.color_pair(2))
#         stdscr.addstr(7, 2, "Press 'q' to exit", curses.A_DIM)

#         stdscr.refresh()

#         # Handle key input
#         key = stdscr.getch()
#         if key == ord('q'):
#             break
        
#         time.sleep(0.5)

# # Run the TUI application
# curses.wrapper(gps_reader)

import curses
from serial import Serial
from pynmeagps import NMEAReader  # type: ignore
import time

def gps_reader(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(1)   # Non-blocking input
    stdscr.timeout(500) # Refresh every 500ms

    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    local_data = "Waiting for local GPS data..."
    waypoint_data = "Waiting for waypoint data..."

    with Serial('/dev/ttyS0', 9600, timeout=3) as stream:
        nmr = NMEAReader(stream)

        while True:
            if stream.in_waiting > 0:  # Read only if data is available
                try:
                    raw_data, parsed_data = nmr.read()
                    print(f"DEBUG: {raw_data}")  # Print raw GPS data for debugging

                    if parsed_data:
                        if parsed_data.msgID == "GNGGA":
                            local_data = f"Lat: {parsed_data.lat} {parsed_data.NS}, Lon: {parsed_data.lon} {parsed_data.EW}, Alt: {parsed_data.alt} {parsed_data.altUnit}"
                        elif parsed_data.msgID == "GNWPL":
                            waypoint_data = f"Waypoint: {parsed_data.wpt}, Lat: {parsed_data.lat} {parsed_data.NS}, Lon: {parsed_data.lon} {parsed_data.EW}"
                except Exception as e:
                    local_data = f"Error: {str(e)}"

            # Refresh UI
            stdscr.clear()
            stdscr.addstr(1, 2, "GPS Terminal Interface", curses.A_BOLD)

            max_width = curses.COLS - 4
            stdscr.addstr(3, 2, f"Local GPS Data: {local_data[:max_width]}", curses.color_pair(1))
            stdscr.addstr(5, 2, f"Remote Waypoint Data: {waypoint_data[:max_width]}", curses.color_pair(2))

            stdscr.addstr(7, 2, "Press 'q' to exit", curses.A_DIM)
            stdscr.refresh()

            if stdscr.getch() == ord('q'):
                break

            time.sleep(0.5)

curses.wrapper(gps_reader)
