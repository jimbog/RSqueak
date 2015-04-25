set -ex
sudo apt-get update

# install arm environment
sudo apt-get install -y debootstrap schroot binfmt-support qemu-system qemu-user-static scratchbox2 gcc-arm-linux-gnueabi libsdl1.2-dev libffi-dev
mkdir precise_arm
sudo chown $USER /etc/schroot/schroot.conf
echo "
[precise_arm]
directory=$PWD/precise_arm
users=$USER
root-users=$USER
groups=$USER
aliases=default
type=directory
" >>  /etc/schroot/schroot.conf
cat /etc/schroot/schroot.conf
sudo chown root /etc/schroot/schroot.conf

sudo qemu-debootstrap --variant=buildd --arch=armel precise precise_arm/ http://ports.ubuntu.com/ubuntu-ports/
schroot -c precise_arm -- uname -m
sudo su -c 'echo "deb http://ports.ubuntu.com/ubuntu-ports/ precise main universe restricted" > precise_arm/etc/apt/sources.list'
schroot -c precise_arm -u root -- apt-get update
schroot -c precise_arm -u root -- apt-get install -y libffi-dev python-dev build-essential libsdl1.2-dev
cd precise_arm/
sb2-init -c `which qemu-arm` ARM `which arm-linux-gnueabi-gcc`
cd ..

# need a 32-bit pypy
sudo apt-get install -y libffi6:i386 libc6:i386 libbz2-1.0:i386 libexpat1:i386 zlib1g:i386 libssl1.0.0:i386 libgcrypt11:i386 libtinfo5:i386
wget https://bitbucket.org/pypy/pypy/downloads/pypy-2.5.1-linux.tar.bz2
tar xjf pypy-2.5.1-linux.tar.bz2
rm pypy-2.5.1-linux.tar.bz2
mv pypy-2.5.1* pypy-linux
pypy-linux/bin/pypy -c 'import sys; print "HELLO " + str(sys.maxint)'
