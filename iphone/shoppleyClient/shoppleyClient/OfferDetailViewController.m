//
//  OfferDetailViewController.m
//  shoppleyClient
//
//  Created by yod on 6/18/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "OfferDetailViewController.h"

#import "SLCurrentOffer.h"
#import "SLTableViewDataSource.h"
#import "SLTableItem.h"

@implementation OfferDetailViewController

- (id)initWithNavigatorURL:(NSURL*)URL query:(NSDictionary*)query {
    if ((self = [super init])) {
        _offer = [query objectForKey:@"offer"];
        self.title = _offer.name;
           
        self.tableViewStyle = UITableViewStyleGrouped;
        self.variableHeightRows = YES;
    }
    return self;
}

- (void)dealloc {
    TT_RELEASE_SAFELY(_offer);
    [super dealloc];
}

- (void)createModel {
    // [[UIApplication sharedApplication] canOpenURL:(NSString*)someURL]
    self.dataSource = [SLSectionedDataSource dataSourceWithObjects:
                       @"",
                       [TTTableTextItem itemWithText:@"Call" URL:@"tel:8574458979"],//[NSString stringWithFormat:@"tel:%@", _offer.phone]],
                       [TTTableTextItem itemWithText:@"Locate" URL:nil],
                       @"",
                       [SLRightValueTableItem itemWithText:@"Your personal redeem code" value:_offer.code],
                       @"",
                       [TTTableTextItem itemWithText:@"Forward to Friends (10 points)" URL:nil],
                       nil
                       ];
}

- (void)viewWillAppear:(BOOL)animated {
    UIView* headerView = [[[OfferDetailHeaderView alloc] initWithFrame:CGRectMake(0, 0, 320, 50) offer:_offer] autorelease];
    self.tableView.tableHeaderView = headerView;
    [super viewWillAppear:animated];
}

@end

@implementation OfferDetailHeaderView

- (id)initWithFrame:(CGRect)frame offer:(SLOffer*)offer {
    if ((self = [super initWithFrame:frame])) {
        static const CGFloat kImageWidth = 50;
        static const CGFloat kImageHeight = 50;
        static const CGFloat kSmallMargin = 7;
        static const CGFloat kLargeMargin = 10;
        
        self.backgroundColor = [UIColor clearColor];
        
        TTImageView* imageView = [[[TTImageView alloc] init] autorelease];
        imageView.urlPath = offer.img;        
        imageView.frame = CGRectMake(kSmallMargin, kSmallMargin, kImageWidth, kImageHeight);
        [self addSubview:imageView];
        
        CGFloat left = kSmallMargin + kImageWidth + kLargeMargin;
        
        TTStyledTextLabel* titleLabel = [[[TTStyledTextLabel alloc] initWithFrame:CGRectMake(left, kSmallMargin, frame.size.width - left - kSmallMargin, 100)] autorelease];
        titleLabel.font = [UIFont systemFontOfSize:17];
        NSString* title = [NSString stringWithFormat:@"<b>%@</b> by %@", offer.name, offer.merchantName];
        titleLabel.text = [TTStyledText textFromXHTML:title lineBreaks:YES URLs:YES];
        titleLabel.contentInset = UIEdgeInsetsMake(0, 0, 0, 0);
        [titleLabel sizeToFit];
        titleLabel.backgroundColor = self.backgroundColor;
        [self addSubview:titleLabel];
        
        CGFloat top = kSmallMargin + MAX(titleLabel.frame.size.height, kImageHeight) + kLargeMargin;
        TTStyledTextLabel* detailLabel = [[[TTStyledTextLabel alloc] initWithFrame:CGRectMake(kSmallMargin, top, frame.size.width - (2*kSmallMargin), 100)] autorelease];
        detailLabel.font = [UIFont systemFontOfSize:14];
        NSString* detail = offer.description;
        detailLabel.text = [TTStyledText textFromXHTML:detail lineBreaks:YES URLs:YES];
        detailLabel.contentInset = UIEdgeInsetsMake(0, 0, 0, 0);
        [detailLabel sizeToFit];
        detailLabel.backgroundColor = self.backgroundColor;
        [self addSubview:detailLabel];
        
        top += detailLabel.frame.size.height + kSmallMargin;
        
        TTStyledTextLabel* redLabel = [[[TTStyledTextLabel alloc] initWithFrame:CGRectMake(kSmallMargin, top, frame.size.width - (2*kSmallMargin), 100)] autorelease];
        redLabel.font = [UIFont systemFontOfSize:14];
        NSString* redLabelText = @"";
        if ([offer isKindOfClass:[SLCurrentOffer class]]) {
            redLabelText = [NSString stringWithFormat:@"<b>expires: %@</b>", ((SLCurrentOffer*)offer).expires];
        }
        redLabel.text = [TTStyledText textFromXHTML:redLabelText lineBreaks:YES URLs:YES];
        redLabel.contentInset = UIEdgeInsetsMake(0, 0, 0, 0);
        [redLabel sizeToFit];
        redLabel.backgroundColor = self.backgroundColor;
        [self addSubview:redLabel];
        
        // Resize
        frame.size.height = top + redLabel.frame.size.height + kLargeMargin;
        self.frame = frame;
    }
    return self;
}

- (void)dealloc {
    TT_RELEASE_SAFELY(_offer);
    [super dealloc];
}

@end
