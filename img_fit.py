def bestFitImageSize( img_width, img_height, win_width, win_height ):

    def doesFit( iw, ih, ww, wh ):
        return iw <= ww and ih <= wh

    while( not doesFit( img_width, img_height, win_width, win_height ) ):
        img_width /= 2
        img_height /= 2

    return img_width, img_height
