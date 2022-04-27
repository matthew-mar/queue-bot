filename='pids.txt'
filelines=$(cat $filename)
for line in $filelines ; do
    echo "killing procces" $line
    kill $line
done
echo "" > ./pids.txt