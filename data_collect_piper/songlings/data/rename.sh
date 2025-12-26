
cd /home/pc3/data_collect/songlings/data/tmp/cup_1104
i=1
for file in $(ls -v *.hdf5); do
    mv "$file" "episode_${i}.hdf5"
    ((i++))
done