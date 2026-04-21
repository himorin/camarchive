# -*- Mode: perl; indent-tabs-mode: nil -*-
#
# Module for Constants Definitions
#

package PNAPI::Constants;

use strict;

use base qw(Exporter);
use File::Basename;
use Cwd;

@PNAPI::Constants::EXPORT = qw(
  PNAPI_VERSION
  PNAPI_CONFIG

  TRUE
  FALSE

  STATE_QUEUED
  STATE_FIRED
  STATE_DELETED
  STATE_INVALID
  STATE_ERROR
  STATE_PUSHED

  FILES_CONFIRMED_OK

  HTTP_STATUS

  LOCATIONS
  HASH_DIRSIZE
  HASH_PREVIEW
  DEF_LANG

  DB_UNLOCK_ABORT

  FMT_DATE
  FMT_FULL
  IMG_DNAME
  MOV_DNAME
  MOV_EXT
  MOV_MIME
  IMG_FMT
  IMG_FMT_DEF
  IMG_FMT_DEF_IMK
);

# target specific constants
use constant FMT_DATE     => "%Y%m%d";
use constant FMT_FULL     => "%Y%m%d%H%M%S";
use constant IMG_DNAME    => "/image/";
use constant MOV_DNAME    => "/movie/";
use constant MOV_EXT      => ".mp4";
use constant MOV_MIME     => "video/mp4";
use constant IMG_FMT      => {
  'jpg' => 'image/jpeg',
  'png' => 'image/png',
  'gif' => 'image/gif',
};
use constant IMG_FMT_DEF  => 'jpg';
use constant IMG_FMT_DEF_IMK => 'jpeg:-';

use constant TRUE         => 1;
use constant FALSE        => 0;

use constant STATE_QUEUED   => 0;
use constant STATE_FIRED    => 1;
use constant STATE_DELETED  => 2;
use constant STATE_INVALID  => 3;
use constant STATE_ERROR    => 4;
use constant STATE_PUSHED   => 5;

use constant FILES_CONFIRMED_OK => 1;
use constant HASH_DIRSIZE       => 2;

use constant PNAPI_VERSION => "0.1";
use constant PNAPI_CONFIG => "config.json";
use constant HASH_PREVIEW => 'jpg';
use constant DEF_LANG     => 'ja';

use constant HTTP_STATUS  => {
  200 => '200 OK',
  201 => '201 Created',
  204 => '204 No Content',
  302 => '302 Found',
  303 => '303 See Other',
  304 => '304 Not Modified',
  307 => '307 Temporary Redirect',
  400 => '400 Bad Request',
  403 => '403 Forbidden',
  404 => '404 Not Found',
  501 => '501 Not Implemented',
  503 => '503 Service Unavailable',
};

# DB
use constant DB_UNLOCK_ABORT => 1;

# installation locations
# parent
#  => registration/ : script installation (like public_html)
#  => common/ : static configurations
sub LOCATIONS {
    # absolute path for installation ("installation")
    my $inspath = dirname(dirname($INC{'PNAPI/Constants.pm'}));
    # detaint
    $inspath =~ /(.*)/;
    $inspath = $1;
    if ($inspath eq '.') { $inspath = getcwd(); }
    elsif ($inspath eq '..') { $inspath = dirname(getcwd()); }
    return {
        'cgi'        => $inspath,
        'config'     => dirname($inspath) . '/common/',
        'hashdir'    => dirname($inspath) . '/files/',
        'template'   => dirname($inspath) . '/tmpl/',
        'datacache'  => dirname($inspath) . '/datacache/',
    };
}


1;

__END__

