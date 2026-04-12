# Module for Config Loader

package PNAPI::Config;

# just load and profide configurations from LOCATIONS->config/<fname>

use strict;
use lib '.';
use base qw(Exporter);
use JSON;

use PNAPI::Constants;

%PNAPI::Config::EXPORT = qw(
  new
  get
  get_hash
  int_to_secret
  secret_to_int
  GetHashFilename
);

our $params;

sub new {
  my ($self) = @_;
  $self->_read_config_file();
  return $self;
}

sub get {
  my ($self, $name) = @_;
  if (! defined($name)) {return undef; }
  return $params->{$name};
}

sub get_hash {
  my ($self) = @_;
  return $params;
}

sub int_to_secret {
  my ($self, $val) = @_;
  my $ret = '00000000' . sprintf("%X", $val);
  return substr($ret, -8);
}

sub secret_to_int {
  my ($self, $val) = @_;
  return hex $val;
}

sub GetHashFilename {
  my ($self, $target, $is_preview, $isnew) = @_;
  my $hashnum = $self->get('hashdir');
  my $fname = PNAPI::Constants::LOCATIONS()->{'hashdir'} . '/';
  my $hsize = PNAPI::Constants::HASH_DIRSIZE;
  my $tmp = $target;

  for (my $cnt = 0; $cnt < $hashnum; $cnt++) {
    $fname .= substr($tmp, 0, $hsize) . '/';
    $tmp = substr($tmp, $hsize);
  }
  $fname .= $target;
  if ($is_preview) {
    $fname += '.' + PNAPI::Constants::HASH_PREVIEW;
  }

  if ((defined($isnew)) || (-f $fname)) {
    return $fname;
  }
  return undef;
}

#------------------------------- private

sub _read_config_file {
  my ($self) = @_;
  my $config_file = PNAPI::Constants::LOCATIONS()->{'config'} . PNAPI_CONFIG;
  if (-e $config_file) {
    open(INDAT, $config_file);
    my $config_data;
    foreach(<INDAT>) { $config_data .= $_; }
    close(INDAT);
    $params = decode_json($config_data);
  } elsif ($ENV{'SERVER_SOFTWARE'}) {
    require CGI::Carp;
    CGI::Carp->import('fatalsToBrowser');
    die "ERROR: Failed to load site configuration file";
  }
}

1;

__END__

