opts_count=0
while getopts f: flag
do
    case "${flag}" in
        f)                           versionFile=${OPTARG}; ((opts_count=opts_count+1)) ;;
        *)                                     echo "Unknown parameter passed"; exit 1 ;;
    esac
done

usage(){
    echo "**Get Proto Version Script***"
    echo "Usage: ./get_proto_version.sh -f ../protos/version.txt"
    echo "---Parameters---"
    echo "f=    :proto version file"
}

getProtoVersion() {
    local protoVersionFile=$1

    if [ ! -f "$protoVersionFile" ]; then
        echo "$protoVersionFile does not exist."
        exit 1
    fi

    versionLine=$(head -n 1 $protoVersionFile)

    if [[ $versionLine =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "##vso[task.setvariable variable=protoVersion;]$versionLine"
    else
        echo "$versionLine is not valid."
        exit 1
    fi
}

start() {
    getProtoVersion $versionFile
}

# Exit if we don't get arguements
[[ $opts_count < 1 ]] && { usage && exit 1; } || start
