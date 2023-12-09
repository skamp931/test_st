import time 
import streamlit as st

def main():
    status_area = st.empty()

    count_down_sec = 7
    for i in range(count_down_sec):
        status_area.write(f"{count_down_sec -i}sec left")

        time.sleep(1)
    
    status_area.write("Done!")

    st.balloons()

if __name__ == "__main__":
    main()
