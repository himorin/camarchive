# Module for backend mysql

package PNAPI::DBmysql;
use strict;
use lib '.';
use PNAPI::DB;
use base qw(PNAPI::DB);

use PNAPI::Constants;
use PNAPI::Config;

sub new {
  my ($class, $user, $pass, $host, $dbname, $port, $sock) = @_;
  my $dsn = "DBI:mysql:host=$host;database=$dbname";
  $dsn .= ";port=$port" if $port;
  $dsn .= ";mysql_socket=$sock" if $sock;
  my %attrs = ( mysql_enable_utf8 => 1);
  my $self = $class->db_new_conn($dsn, $user, $pass, \%attrs);
  bless($self, $class);
  $self->do("SET NAMES utf8");
  return $self;
}

#------------------------------- private


1;

__END__

