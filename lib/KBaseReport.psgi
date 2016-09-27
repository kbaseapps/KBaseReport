use KBaseReport::KBaseReportImpl;

use KBaseReport::KBaseReportServer;
use Plack::Middleware::CrossOrigin;



my @dispatch;

{
    my $obj = KBaseReport::KBaseReportImpl->new;
    push(@dispatch, 'KBaseReport' => $obj);
}


my $server = KBaseReport::KBaseReportServer->new(instance_dispatch => { @dispatch },
				allow_get => 0,
			       );

my $handler = sub { $server->handle_input(@_) };

$handler = Plack::Middleware::CrossOrigin->wrap( $handler, origins => "*", headers => "*");
