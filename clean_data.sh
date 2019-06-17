# Dedup cache collected
cp data/cache.txt data/cache.txt.bak
sort -u data/cache.txt > /tmp/sorted_cache.txt
mv /tmp/sorted_cache.txt data/cache.txt

# youtube_giveaway_commentlinks = youtube_giveaway_commentlinks - cached
comm -23 data/youtube_giveaway_commentlinks.txt data/cache.txt > /tmp/pending.txt
mv /tmp/pending.txt data/youtube_giveaway_commentlinks.txt
# gshuf -o data/youtube_giveaway_commentlinks.txt < data/youtube_giveaway_commentlinks.txt

# Dedup youtube_giveaway_commentlinks
cp data/youtube_giveaway_commentlinks.txt data/youtube_giveaway_commentlinks.txt.bak
sort -u data/youtube_giveaway_commentlinks.txt > /tmp/sorted_youtube_giveaway_commentlinks.txt
mv /tmp/sorted_youtube_giveaway_commentlinks.txt data/youtube_giveaway_commentlinks.txt
