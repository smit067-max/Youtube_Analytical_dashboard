import streamlit as st
import pandas as pd
import plotly.express as px
from googleapiclient.discovery import build

# Page Configuration
st.set_page_config(
    page_title="YouTube Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 YouTube Analytics Dashboard")
st.write("Analyze YouTube channel performance and video engagement.")

# Sidebar

st.sidebar.header("Dashboard Controls")
channel_name = st.sidebar.text_input("Enter YouTube Channel Name")

# YouTube API
API_KEY = "AIzaSyCV984ecMGLjwzEKswchSZ3DCfxfRm3ZkI"

youtube = build("youtube", "v3", developerKey=API_KEY)

# Get Channel ID
def get_channel_id(channel_name):

    request = youtube.search().list(
        part="snippet",
        q=channel_name,
        type="channel",
        maxResults=1
    )

    response = request.execute()

    channel_id = response["items"][0]["snippet"]["channelId"]

    return channel_id

# Get Channel Info
def get_channel_info(channel_id):

    request = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    )

    response = request.execute()

    item = response["items"][0]

    return {
        "title": item["snippet"]["title"],
        "logo": item["snippet"]["thumbnails"]["high"]["url"],
        "Subscribers": int(item["statistics"]["subscriberCount"]),
        "Views": int(item["statistics"]["viewCount"]),
        "Videos": int(item["statistics"]["videoCount"])
    }


# Get Videos
def get_videos(channel_id):

    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=20,
        order="date"
    )

    response = request.execute()

    video_data = []

    for item in response["items"]:

        if item["id"]["kind"] == "youtube#video":

            video_data.append({
                "VideoID": item["id"]["videoId"],
                "Title": item["snippet"]["title"],
                "Thumbnail": item["snippet"]["thumbnails"]["high"]["url"]
            })

    return video_data

# Get Video Stats
def get_video_stats(video_data):

    ids = [video["VideoID"] for video in video_data]

    request = youtube.videos().list(
        part="statistics",
        id=",".join(ids)
    )

    response = request.execute()

    stats = []

    for i, video in enumerate(response["items"]):

        stat = video["statistics"]

        stats.append({
            "Title": video_data[i]["Title"],
            "Thumbnail": video_data[i]["Thumbnail"],
            "Views": int(stat.get("viewCount",0)),
            "Likes": int(stat.get("likeCount",0)),
            "Comments": int(stat.get("commentCount",0))
        })

    df = pd.DataFrame(stats)

    return df


# Dashboard

if channel_name:

    channel_id = get_channel_id(channel_name)

    channel = get_channel_info(channel_id)

    # Channel header
    colA, colB = st.columns([1,4])

    with colA:
        st.image(channel["logo"])

    with colB:
        st.header(channel["title"])

    st.divider()

    # Metrics
    col1, col2, col3 = st.columns(3)

    col1.metric("Subscribers", f"{channel['Subscribers']:,}")
    col2.metric("Total Views", f"{channel['Views']:,}")
    col3.metric("Total Videos", f"{channel['Videos']:,}")

    st.divider()

    # Get videos
    videos = get_videos(channel_id)

    df = get_video_stats(videos)

    df["Engagement Rate"] = (df["Likes"] + df["Comments"]) / df["Views"]

    
    # Top Videos Chart
    
    st.subheader("Top Performing Videos")

    top_videos = df.sort_values(
        by="Views",
        ascending=False
    ).head(10)

    fig_top = px.bar(
        top_videos,
        x="Title",
        y="Views",
        color="Views",
        title="Top 10 Videos by Views"
    )

    st.plotly_chart(fig_top, use_container_width=True)

    
    # Likes Trend
    
    st.subheader("Likes Trend")

    fig_likes = px.line(
        df,
        y="Likes",
        title="Likes Trend",
        markers=True
    )

    st.plotly_chart(fig_likes, use_container_width=True)

    
    # Engagement Analysis
    
    st.subheader("Engagement Analysis")

    fig_engagement = px.scatter(
        df,
        x="Views",
        y="Engagement Rate",
        size="Likes",
        hover_name="Title",
        title="Engagement vs Views"
    )

    st.plotly_chart(fig_engagement, use_container_width=True)

    st.divider()

    
    # Video Cards (Thumbnail + Title)
    
    st.subheader("Recent Videos")

    cols = st.columns(4)

    for i, video in enumerate(df.head(8).to_dict("records")):

        with cols[i % 4]:
            st.image(video["Thumbnail"])
            st.write(video["Title"])
            st.caption(f"Views: {video['Views']:,}")

    st.divider()

    
    # Data Table
    
    st.subheader("Video Analytics Data")

    st.dataframe(df, use_container_width=True)

# Footer

st.markdown("---")
st.markdown("Dashboard built with **Streamlit + YouTube Data API**")