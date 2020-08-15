declare -a profiles=(mindfulmft minaa_b risingwoman seerutkchawla themindgeek the.holistic.psychologist nedratawwab millennial.therapist yasminecheyenne alyssamariewellness dr.marielbuque sitwithwhit dr.alexandra.solomon thebraincoach heydrjustine lauraandersontherapy lizlistens findmywellbeing)

set -e

source ~/anaconda3/bin/activate ds

for profile in ${profiles[*]}; do
    instaloader $profile --no-profile-pic --no-videos --no-video-thumbnails --no-compress-json
done
